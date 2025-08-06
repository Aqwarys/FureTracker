from django.shortcuts import render
from promotions.models import Promotion


def promotion_list(request):
    promotion = Promotion.objects.filter(is_active=True).order_by('-order', '-created_at')
    return render(request, 'promotions/promotions_list.html', {'promotion': promotion})