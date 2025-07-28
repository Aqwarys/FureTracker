# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Order, Review, Comment, OrderStatus, OrderMedia
from .forms import ReviewForm, CommentForm, OrderTrackingForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_filters.views import FilterView

from orders.filters import OrderFilter




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

    comments = order.comments.filter(moderated=True).order_by('created_at')
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
