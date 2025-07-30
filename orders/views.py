import boto3
import os
import uuid
import json
import mimetypes

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db import transaction

from orders.models import Order, Comment, OrderMedia
from orders.forms import CommentForm, OrderMediaForm
from orders.filters import OrderFilter
from core.models import OrderStatus

import logging

logger = logging.getLogger(__name__)


s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)


def order_list(request):

    logger.info("Запрошено список заказов")
    qs = Order.objects.all().select_related('order_status')

    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(order_number__icontains=search)
        logger.debug(f"Поиск по номеру заказа: {search}")

    order_filter = OrderFilter(request.GET, queryset=qs)

    paginator = Paginator(order_filter.qs, 5)
    page_number = request.GET.get('page')
    order_page = paginator.get_page(page_number)

    if not order_page.object_list:
        logger.warning("Список заказов пуст или не найдено результатов по фильтру.")

    context = {
        'filter': order_filter,
        'orders_count': order_page.paginator.count,
        'orders': order_page
    }
    return render(request, 'orders/order_list.html', context)


def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related('order_status'),
        order_number=order_number
    )
    logger.info(f"Запрошена страница заказа {order_number}")

    if request.method == 'POST':
        logger.info("Отправлен комментарий")
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            logger.info("Комментарий прошел валидацию")
            new_comment = comment_form.save(commit=False)
            new_comment.order = order
            new_comment.save()
            logger.info("Комментарий сохранен")
            return redirect(f"{reverse('orders:public_order_detail', args=[order.order_number])}#comments-section")
    else:
        comment_form = CommentForm()

    order_media_form = OrderMediaForm()


    comments = order.comments.filter(moderated=True).order_by('created_at')
    order_media = OrderMedia.objects.filter(order=order).select_related('order_stage').order_by('uploaded_at')
    logger.info("Получены комментарии и медиа")

    all_order_statuses = OrderStatus.objects.all().order_by('order_index')

    context = {
        'order': order,
        'comments': comments,
        'comment_form': comment_form,
        'order_media': order_media,
        'all_order_statuses': all_order_statuses,
        'order_media_form': order_media_form,
    }
    return render(request, 'orders/order_detail.html', context)


@csrf_protect
@require_POST
def get_s3_presigned_url(request):
    try:
        data = json.loads(request.body)
        filename = data.get('filename')
        filetype = data.get('filetype')
        order_number = data.get('order_number')
        logger.info(f"Запрос на получение предписанного URL для файла {filename} типа {filetype}")

        if not all([filename, filetype, order_number]):
            return JsonResponse({'error': 'Missing filename, filetype, or order_number.'}, status=400)

        allowed_mimetypes = ['image/', 'video/', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if not any(filetype.startswith(t) for t in allowed_mimetypes):
             return JsonResponse({'error': 'Unsupported file type. Only images, videos, and documents are allowed.'}, status=400)

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)

        guessed_extension = mimetypes.guess_extension(filetype)
        if not guessed_extension:
            _, ext = os.path.splitext(filename)
            guessed_extension = ext if ext else '.bin'

        unique_filename = f"{uuid.uuid4()}{guessed_extension}"

        s3_object_key_for_boto3 = os.path.join(
             "media",
             "orders",
             str(order.order_number),
             unique_filename
         ).replace('\\', '/')

        s3_file_path_for_db = os.path.join(
            "orders",
            str(order.order_number),
            unique_filename
        ).replace('\\', '/')

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_object_key_for_boto3,
                'ContentType': filetype
            },
            ExpiresIn=3600
        )

        return JsonResponse({
            'presigned_url': presigned_url,
            'file_path_on_s3': s3_file_path_for_db
        })
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON в get_s3_presigned_url.", exc_info=True)
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        logger.critical(f"Критическая ошибка в get_s3_presigned_url: {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)


@csrf_protect
@require_POST
def complete_s3_upload(request):
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        s3_file_path = data.get('s3_file_path')
        order_stage_id = data.get('order_stage_id')

        logger.info(f"Запрос на завершение загрузки файла для заказа {order_number}")

        if not all([order_number, s3_file_path, order_stage_id]):
            logger.error("Нету необходимых данных для завершения загрузки файла")
            return JsonResponse({'error': 'Missing required data: order_number, s3_file_path, or order_stage_id.'}, status=400)

        try:
            order_stage_id = int(order_stage_id)
            logger.info(f"ID этапа заказа: {order_stage_id}")
        except ValueError:
            logger.error("Неверный формат ID этапа заказа")
            return JsonResponse({'error': 'Invalid order_stage_id format.'}, status=400)

        with transaction.atomic():
            order = get_object_or_404(Order, order_number=order_number)
            order_status = get_object_or_404(OrderStatus, pk=order_stage_id)
            logger.info(f"Этап заказа: {order_status}")

            media_instance = OrderMedia(
                order=order,
                order_stage=order_status,
            )
            media_instance.file.name = s3_file_path
            media_instance.save()
            logger.info(f"Медиафайл сохранен: {media_instance}")

        logger.info("Завершено сохранение медиафайла")
        return JsonResponse({'status': 'success', 'message': 'File metadata saved.', 'media_url': media_instance.file.url})
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON в complete_s3_upload.", exc_info=True)
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        logger.critical(f"Критическая ошибка в complete_s3_upload: {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)