from django.contrib import admin
from core.models import OrderStatus, SiteSettings, FAQ

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



@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """
    Кастомная административная панель для модели FAQ.
    Улучшает отображение, поиск и редактирование вопросов и ответов.
    """
    list_display = (
        'get_truncated_question',
        'get_truncated_answer',
        'order',
    )

    search_fields = (
        'question',
        'answer',
    )


    ordering = ('order', 'question',)

    fieldsets = (
        (None, {
            'fields': ('question', 'answer',)
        }),
        ('Настройки отображения', {
            'fields': ('order',),
            'classes': ('collapse',),
            'description': 'Установите порядок отображения вопроса.'
        }),
    )

    list_per_page = 25

    def get_truncated_question(self, obj):
        """Возвращает укороченный вопрос для отображения в списке."""
        return obj.question[:75] + '...' if len(obj.question) > 75 else obj.question
    get_truncated_question.short_description = 'Вопрос' 

    def get_truncated_answer(self, obj):
        """Возвращает укороченный ответ для отображения в списке."""
        return obj.answer[:100] + '...' if len(obj.answer) > 100 else obj.answer
    get_truncated_answer.short_description = 'Ответ'