from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path('healthz/', lambda request: HttpResponse('ok', content_type='text/plain'), name='healthz'),
    path('admin/', admin.site.urls, name='admin'),
    path('', include('main.urls')),
    path('orders/', include('orders.urls')),
    path('promotions/', include('promotions.urls')),
]
