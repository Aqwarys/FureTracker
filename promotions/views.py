from django.shortcuts import render
from promotions.models import Promotion
from django.views.generic import ListView


class PromotionsListView(ListView):
    model = Promotion
    template_name = 'promotions/promotions_list.html'
    context_object_name = 'promotions'