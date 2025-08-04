from django.urls import path
from promotions import views
app_name = 'promotions'

urlpatterns = [
    path('', views.PromotionsListView.as_view(), name='promotions_list'),
]