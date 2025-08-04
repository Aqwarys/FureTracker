from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('main.urls')),
    path('orders/', include('orders.urls')),
    path('promotions/', include('promotions.urls')),
]
