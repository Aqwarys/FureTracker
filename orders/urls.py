from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('<str:order_number>/', views.order_detail, name='public_order_detail'),

    path('api/get-s3-presigned-url/', views.get_s3_presigned_url, name='get_s3_presigned_url'),
    path('api/complete-s3-upload/', views.complete_s3_upload, name='complete_s3_upload'),
]