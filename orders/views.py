# orders/views.py
import boto3, os, uuid, json
import mimetypes

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.forms.models import model_to_dict
from django.core.files.storage import default_storage

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from orders.models import Order, Review, Comment, OrderStatus, OrderMedia
from orders.forms import ReviewForm, CommentForm, OrderMediaForm
from core.models import OrderStatus
from django.core.paginator import Paginator

from orders.filters import OrderFilter


s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)


def order_list(request):
    qs = Order.objects.all()

    # Поиск
    search = request.GET.get('search')
    if search:
        qs = qs.filter(order_number__icontains=search)

    # Фильтры
    order_filter = OrderFilter(request.GET, queryset=qs)

    paginator = Paginator(order_filter.qs, 5)
    page_number = request.GET.get('page')
    order_page = paginator.get_page(page_number)

    context = {
        'filter': order_filter,
        'orders_count': order_filter.qs.count(),
        'orders': order_page
    }
    return render(request, 'orders/order_list.html', context)


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.order = order
            new_comment.save()
            return redirect(reverse('orders:public_order_detail', args=[order.order_number]) + '#comments-section')
    else:
        comment_form = CommentForm()
        order_media_form = OrderMediaForm()

    comments = order.comments.filter(moderated=True).order_by('created_at')
    order_media = OrderMedia.objects.filter(order=order).order_by('uploaded_at')

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

        if not filename or not filetype or not order_number:
            return JsonResponse({'error': 'Missing filename, filetype, or order_number'}, status=400)

        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found.'}, status=404)

        _, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4()}{ext}"

        # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ ЗДЕСЬ ---
        # ЯВНО ДОБАВЛЯЕМ "media" в путь для S3 Boto3
        # os.path.join() справится с прямыми/обратными слешами, а затем мы все приведем к прямым.
        s3_object_key_for_boto3 = os.path.join(
            "media",                     # <--- ДОБАВИЛИ "media" СЮДА!
            "orders",
            str(order.order_number),
            unique_filename
        ).replace('\\', '/') # И обязательно приводим к прямым слэшам

        # Путь для базы данных (FileField.name) НЕ ДОЛЖЕН содержать "media/",
        # так как это будет добавлено автоматически через settings.STORAGES.
        s3_file_path_for_db = os.path.join(
            "orders",
            str(order.order_number),
            unique_filename
        ).replace('\\', '/') # И тоже приводим к прямым слэшам

        if not filetype:
            filetype, _ = mimetypes.guess_type(filename) or ('application/octet-stream', None)

        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': s3_object_key_for_boto3, # Теперь этот ключ будет media/orders/ORD-.../
                'ContentType': filetype
            },
            ExpiresIn=3600
        )

        return JsonResponse({
            'presigned_url': presigned_url,
            'file_path_on_s3': s3_file_path_for_db # Этот путь будет orders/ORD-.../
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

@csrf_protect
@require_POST
def complete_s3_upload(request):
    try:
        data = json.loads(request.body)
        order_number = data.get('order_number')
        s3_file_path = data.get('s3_file_path') # Это 'orders/ORD-000011/filename.ext'
        order_stage_id = data.get('order_stage_id')

        if not order_number or not s3_file_path or not order_stage_id:
            return JsonResponse({'error': 'Missing required data: order_number, s3_file_path, or order_stage_id'}, status=400)

        try:
            order = get_object_or_404(Order, order_number=order_number)
            order_status = get_object_or_404(OrderStatus, pk=order_stage_id)
        except (Order.DoesNotExist, OrderStatus.DoesNotExist):
            return JsonResponse({'error': 'Order or OrderStatus not found.'}, status=404)

        media_instance = OrderMedia(
            order=order,
            order_stage=order_status,
        )
        # Django FileField теперь сам использует 'order_media_upload_to'
        # и сформирует полный путь на основе 's3_file_path' (он же orders/ORD-.../)
        media_instance.file.name = s3_file_path
        media_instance.save()

        return JsonResponse({'status': 'success', 'message': 'File metadata saved.', 'media_url': media_instance.file.url})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)