from django.contrib import admin
from core.models import OrderStatus

admin.site.site_header = "Панель управления Бизнесом"
admin.site.site_title = "Управление Заказами и Контентом"
admin.site.index_title = "Добро пожаловать в админ-панель"

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index')
    ordering = ['order_index']
    search_fields = ['name']
    list_filter = ['order_index']