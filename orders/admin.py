from django.contrib import admin
from orders.models import Order, OrderMedia, Comment, Review

from django.utils.html import format_html
from django.urls import reverse

# orders/admin.py
from django.contrib import admin
from .models import Order, OrderMedia, Comment, Review
from core.models import OrderStatus # Важно: импортируем OrderStatus из core
# from django.urls import reverse # Пока не нужна, пока закомментированы ссылки
# from django.utils.html import format_html # Пока не нужна

# --- Inlines (только для того, что менеджер УПРАВЛЯЕТ напрямую через Заказ) ---

class OrderMediaInline(admin.TabularInline):
    """
    Позволяет менеджеру добавлять и просматривать медиафайлы, привязанные к заказу
    и его этапам, прямо на странице редактирования заказа.
    """
    model = OrderMedia
    extra = 1 # Сколько пустых форм для добавления показать по умолчанию
    fields = ('file', 'order_stage')
    readonly_fields = ('uploaded_at',) # Поле для чтения, так как генерируется автоматически

class ReviewInline(admin.TabularInline):
    """
    Позволяет менеджеру добавлять и просматривать отзывы, привязанные к заказу
    и его этапам, прямо на странице редактирования заказа.
    """
    model = Review
    extra = 1 # Сколько пустых форм для добавления показать по умолчанию
    fields = ('rating', 'text', 'created_at', 'is_published')
    readonly_fields = ('created_at',)

# --- Основной класс OrderAdmin ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Настройки административной панели для модели Заказ (Order).
    Основное управление информацией о заказе и его статусе.
    """
    list_display = (
        'order_number', 'client_name', 'client_phone',
        'order_status', 'is_completed', 'created_at', 'updated_at',
        # 'get_personal_link', # Закомментируем, пока нет URL-ов. Добавим, когда будет View.
        # 'get_review_status'  # Закомментируем, т.к. отображение статуса отзыва будет в ReviewAdmin
    )
    list_filter = ('order_status', 'is_completed', 'created_at')
    search_fields = ('order_number', 'client_name', 'client_phone', 'description')
    date_hierarchy = 'created_at'
    list_per_page = 25

    # Поля, которые можно только читать на форме редактирования (нельзя изменить)
    readonly_fields = ('order_number', 'access_token', 'created_at', 'updated_at')

    # Расположение полей на форме редактирования/создания заказа
    fieldsets = (
        (None, { # Основная информация о заказе
            'fields': (
                ('order_number', 'order_status', 'is_completed'),
                'description',
                'access_token', # Поле access_token, которое будет readonly
            )
        }),
        ('Информация о клиенте', { # Контактные данные клиента
            'fields': ('client_name', ('client_phone', 'client_email')),
        }),
        ('Временные метки', { # Даты создания и обновления
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',), # Можно свернуть эту секцию
        }),
    )

    # Встраивание связанных моделей, которые менеджер должен непосредственно УПРАВЛЯТЬ здесь
    inlines = [
        OrderMediaInline,
        ReviewInline
    ]

    # # Закомментированные кастомные методы для get_personal_link,
    # # которые будут добавлены, когда появятся соответствующие URLы и View.
    # def get_personal_link(self, obj):
    #     if obj.access_token and obj.order_number:
    #         # from django.urls import reverse
    #         # from django.utils.html import format_html
    #         # from django.urls import NoReverseMatch
    #         try:
    #             link = reverse('order_personal_access', args=[obj.order_number, obj.access_token])
    #             return format_html('<a href="{}" target="_blank">Ссылка клиента</a>', link)
    #         except NoReverseMatch:
    #             return "Ссылка не настроена"
    #     return "Нет (номер заказа не сгенерирован)"
    # get_personal_link.short_description = "Персональная ссылка"


# --- Admin для других моделей (с акцентом на модерацию) ---

# Это должно быть в core/admin.py
# from django.contrib import admin
# from .models import OrderStatus
# @admin.register(OrderStatus)
# class OrderStatusAdmin(admin.ModelAdmin):
#     list_display = ('name', 'order_index', 'description')
#     list_editable = ('order_index',)
#     search_fields = ('name',)
#     list_per_page = 10 # Компактный список

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Настройки административной панели для модели Комментарий.
    Основное назначение: модерация комментариев, оставленных клиентами.
    """
    list_display = ('order', 'author_name', 'text_preview', 'created_at', 'moderated')
    list_filter = ('moderated', 'created_at')
    search_fields = ('text', 'author_name', 'order__order_number') # Поиск по номеру заказа
    readonly_fields = ('order', 'author_name', 'created_at') # Эти поля нельзя редактировать
    actions = ['mark_as_moderated', 'mark_as_unmoderated'] # Действия для пакетной модерации

    # Метод для отображения превью текста в списке (чтобы не загромождать)
    def text_preview(self, obj):
        return obj.text[:75] + '...' if len(obj.text) > 75 else obj.text
    text_preview.short_description = "Текст комментария"

    def mark_as_moderated(self, request, queryset):
        queryset.update(moderated=True)
        self.message_user(request, "Выбранные комментарии успешно одобрены.")
    mark_as_moderated.short_description = "Одобрить выбранные комментарии"

    def mark_as_unmoderated(self, request, queryset):
        queryset.update(moderated=False)
        self.message_user(request, "Выбранные комментарии отклонены.")
    mark_as_unmoderated.short_description = "Отклонить выбранные комментарии"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Настройки административной панели для модели Отзыв.
    Основное назначение: модерация и публикация отзывов, оставленных клиентами.
    """
    list_display = ('order', 'rating', 'text_preview', 'created_at', 'is_published')
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('text', 'order__order_number')
    readonly_fields = ('order', 'rating', 'created_at') # Эти поля нельзя редактировать
    actions = ['publish_reviews', 'unpublish_reviews'] # Действия для пакетной публикации/скрытия

    # Метод для отображения превью текста в списке
    def text_preview(self, obj):
        return obj.text[:75] + '...' if len(obj.text) > 75 else obj.text
    text_preview.short_description = "Текст отзыва"

    def publish_reviews(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, "Выбранные отзывы успешно опубликованы.")
    publish_reviews.short_description = "Опубликовать выбранные отзывы"

    def unpublish_reviews(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Выбранные отзывы сняты с публикации.")
    unpublish_reviews.short_description = "Снять с публикации выбранные отзывы"


# --- consultations/admin.py ---
# Этот класс должен быть в consultations/admin.py
# from django.contrib import admin
# from .models import ConsultationRequest

# @admin.register(ConsultationRequest)
# class ConsultationRequestAdmin(admin.ModelAdmin):
#     list_display = ('name', 'phone', 'message_preview', 'created_at', 'is_processed')
#     list_filter = ('is_processed', 'created_at')
#     search_fields = ('name', 'phone', 'message')
#     readonly_fields = ('created_at',)
#     actions = ['mark_as_processed', 'mark_as_unprocessed']
#
#     def message_preview(self, obj):
#         return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
#     message_preview.short_description = "Сообщение"
#
#     def mark_as_processed(self, request, queryset):
#         queryset.update(is_processed=True)
#         self.message_user(request, "Выбранные заявки помечены как обработанные.")
#     mark_as_processed.short_description = "Пометить как обработанные"
#
#     def mark_as_unprocessed(self, request, queryset):
#         queryset.update(is_processed=False)
#         self.message_user(request, "Выбранные заявки помечены как необработанные.")
#     mark_as_unprocessed.short_description = "Пометить как необработанные"