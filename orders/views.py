# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Order, Review, Comment, OrderStatus, OrderMedia
from .forms import ReviewForm, CommentForm, OrderTrackingForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




# Фильтрация/Поиск: Если это список для менеджера (вне админки), ему может понадобиться фильтровать или искать заказы.

# Выборка только необходимых полей: Для оптимизации запросов к базе данных, можно использовать .only() или .values().

# Сортировка: Заказы могут быть отсортированы по дате, статусу, имени клиента и т.д.
def order_list(request):
    all_orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(all_orders, 10)
    page = request.GET.get('page')
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'orders/order_list.html', {'orders': orders})


def order_detail(request, order_number):
    """
    Displays the details of a specific order, including its progress,
    associated media, and moderated comments. Also handles comment submission.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.order = order
            new_comment.save()

            return redirect(reverse('public_order_detail', args=[order.order_number]) + '#comments-section')
    else:
        comment_form = CommentForm()

    comments = order.comment_set.filter(moderated=True).order_by('created_at')
    order_media = OrderMedia.objects.filter(order=order).order_by('uploaded_at')

    all_order_statuses = OrderStatus.objects.all().order_by('order_index')

    context = {
        'order': order,
        'comments': comments,
        'comment_form': comment_form,
        'order_media': order_media,
        'all_order_statuses': all_order_statuses,
    }
    return render(request, 'orders/order_detail.html', context)

def order_personal_access(request, order_number, access_token):
    order = get_object_or_404(Order, order_number=order_number, access_token=access_token)

    review_form = None
    comment_form = None
    has_review = False
    existing_review = None

    try:
        existing_review = order.review
        has_review = True
    except Order.review.RelatedObjectDoesNotExist:
        review_form = ReviewForm() # Создаем форму отзыва, если его нет

    comment_form = CommentForm() # Форма для комментария всегда доступна

    if request.method == 'POST':
        if 'submit_review' in request.POST and not has_review:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.order = order
                review.save()
                messages.success(request, "Ваш отзыв успешно отправлен и ожидает модерации!")
                return redirect(reverse('order_personal_access', args=[order_number, access_token]))
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в форме отзыва.")

        elif 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.order = order
                comment.author_name = order.client_name # Автоматически заполняем имя автора
                comment.save()
                messages.success(request, "Ваш комментарий успешно отправлен и ожидает модерации!")
                return redirect(reverse('order_personal_access', args=[order_number, access_token]))
            else:
                messages.error(request, "Пожалуйста, исправьте ошибки в форме комментария.")

    # Медиафайлы
    media_stages = OrderStatus.objects.filter(
        id__in=order.media_items.values_list('order_stage', flat=True)
    ).order_by('order_index')

    media_by_stage = {}
    for stage in media_stages:
        media_by_stage[stage] = order.media_items.filter(order_stage=stage).order_by('uploaded_at')

    # Комментарии (все, так как это личная ссылка клиента)
    comments = order.comment_set.all().order_by('created_at')

    context = {
        'order': order,
        'media_by_stage': media_by_stage,
        'comments': comments,
        'review_form': review_form,
        'has_review': has_review,
        'existing_review': existing_review,
        'comment_form': comment_form,
    }
    return render(request, 'orders/order_personal_access.html', context)