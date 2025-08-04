from django.contrib import admin
from core.models import OrderStatus, SiteSettings

admin.site.site_header = "Панель управления Бизнесом"
admin.site.site_title = "Управление Заказами и Контентом"
admin.site.index_title = "Добро пожаловать в админ-панель"

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_index')
    ordering = ['order_index']
    search_fields = ['name']
    list_filter = ['order_index']




@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    # Запрещаем создание новых объектов
    def has_add_permission(self, request):
        # Если объект уже существует, запрещаем добавление нового
        return not SiteSettings.objects.exists()

    # Запрещаем удаление объекта
    def has_delete_permission(self, request, obj=None):
        return False

    # Группируем поля для удобного отображения в админке
    fieldsets = (
        ('Настройки главной страницы', {
            'fields': ('promo_text', 'main_index_text', 'second_index_text')
        }),
        ('Контактная информация', {
            'fields': ('telephone_number', 'address', 'business_age')
        }),
        ('Социальные сети и ссылки', {
            'fields': ('instagram_link', 'whatsapp_link', 'twogis_link')
        })
    )

    # Используем `list_display` только для отображения в списке,
    # но так как объект всегда один, можно использовать только поле,
    # которое показывает его название.
    list_display = ('__str__',)

    # Также можно добавить help_text в саму модель для пояснений
    # Например:
    # class SiteSettings(...):
    #     promo_text = models.CharField(..., help_text="Текст, который будет отображаться в шапке сайта")