from django.contrib import admin
from core.models import OrderStatus

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index')
    ordering = ['order_index']
    search_fields = ['name']
    list_filter = ['order_index']