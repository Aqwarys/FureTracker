from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<str:order_number>/', views.order_detail, name='public_order_detail'),
    # path('order/<str:order_number>/<uuid:access_token>/', views.order_personal_access, name='order_personal_access'),
]