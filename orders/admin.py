# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q

from .models import Order, OrderMedia, Comment, Review
from core.models import OrderStatus

admin.site.site_header = "Панель управления Бизнесом"
admin.site.site_title = "Управление Заказами и Контентом"
admin.site.index_title = "Добро пожаловать в админ-панель"

class OrderMediaInline(admin.TabularInline):
    model = OrderMedia
    extra = 0
    max_num = 0
    fields = ('order_stage', 'file', 'uploaded_at', 'get_thumbnail_or_preview')
    readonly_fields = ('uploaded_at', 'get_thumbnail_or_preview',)

    def get_thumbnail_or_preview(self, obj):
        if obj.file:
            file_url = obj.file.url
            file_ext = file_url.lower().split('.')[-1]
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return format_html('<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain; border-radius: 4px;" />', file_url)
            elif file_ext in ['mp4', 'mov', 'avi', 'webm']:
                return format_html('<i class="fas fa-video fa-2x" style="color: #6c757d;" title="Видео файл"></i>')
        return format_html('<span style="color: #adb5bd;">Нет файла</span>')
    get_thumbnail_or_preview.short_description = 'Превью'

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('author_name', 'text', 'created_at', 'moderated')
    readonly_fields = ('created_at',)

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    max_num = 1
    fields = ('rating', 'text', 'created_at', 'is_published')
    readonly_fields = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'order_status', 'client_name', 'client_phone',
        'is_completed', 'assigned_employees_short', 'created_at', 'updated_at',
        'get_media_count', 'get_comments_count', 'has_review_status'
    )
    list_filter = ('order_status', 'is_completed', 'created_at')
    search_fields = (
        'order_number', 'description', 'client_name', 'client_email', 'client_phone',
        'order_status__name',
        'assigned_employees'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    save_on_top = True
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('order_number', 'order_status', 'description'),
        }),
        ('Информация о клиенте', {
            'fields': ('client_name', 'client_email', 'client_phone'),
            'description': 'Контактные данные клиента для этого заказа.',
        }),
        ('Управление заказом', {
            'fields': ('assigned_employees',),
            'description': 'Информация о сотрудниках, работающих над заказом.'
        }),
        ('Даты выполнения этапов', {
            'fields': ('stage_measurement_date', 'stage_design_date', 'stage_technologist_date', 'stage_completion_date'),
            'description': 'Даты, когда были выполнены ключевые этапы заказа.'
        }),
        ('Служебная информация', {
            'fields': ('access_token', 'is_completed', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Технические детали заказа, не предназначенные для частого редактирования.'
        }),
    )

    readonly_fields = ('order_number', 'access_token', 'is_completed', 'created_at', 'updated_at')

    inlines = [OrderMediaInline, CommentInline, ReviewInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _media_count=Count('media_items', distinct=True),
            _comments_count=Count('comments', distinct=True),
            _has_review=Count('review', distinct=True)
        )
        return queryset

    def get_media_count(self, obj):
        return obj._media_count
    get_media_count.short_description = 'Медиа (шт.)'
    get_media_count.admin_order_field = '_media_count'

    def get_comments_count(self, obj):
        return obj._comments_count
    get_comments_count.short_description = 'Комментарии (шт.)'
    get_comments_count.admin_order_field = '_comments_count'

    def has_review_status(self, obj):
        if hasattr(obj, 'review'):
            return obj.review.is_published
        return False
    has_review_status.boolean = True
    has_review_status.short_description = 'Отзыв опубликован?'

    def assigned_employees_short(self, obj):
        if obj.assigned_employees:
            return (obj.assigned_employees[:50] + '...') if len(obj.assigned_employees) > 50 else obj.assigned_employees
        return '-'
    assigned_employees_short.short_description = 'Сотрудники'

import os
@admin.register(OrderMedia)
class OrderMediaAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_stage', 'get_file_name', 'get_file_type', 'uploaded_at', 'get_thumbnail_or_preview_list')
    list_filter = ('order_stage', 'uploaded_at')
    search_fields = ('order__order_number', 'order_stage__name')
    autocomplete_fields = ('order',)
    readonly_fields = ('uploaded_at', 'get_thumbnail_or_preview_list',)

    def get_file_name(self, obj):
        return os.path.basename(obj.file.name) if obj.file else '-'
    get_file_name.short_description = 'Имя файла'

    def get_file_type(self, obj):
        if obj.file:
            ext = os.path.splitext(obj.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return 'Изображение'
            elif ext in ['.mp4', '.mov', '.avi', '.webm']:
                return 'Видео'
        return 'Другое'
    get_file_type.short_description = 'Тип файла'

    def get_thumbnail_or_preview_list(self, obj):
        return OrderMediaInline.get_thumbnail_or_preview(self, obj)
    get_thumbnail_or_preview_list.short_description = 'Превью'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('order', 'author_name', 'text_preview', 'created_at', 'moderated')
    list_editable = ('moderated',)
    list_filter = ('moderated', 'created_at')
    search_fields = ('order__order_number', 'author_name', 'text')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('order',)

    def text_preview(self, obj):
        return obj.text[:75] + '...' if len(obj.text) > 75 else obj.text
    text_preview.short_description = 'Текст комментария'

    @admin.action(description='Пометить выбранные комментарии как "Модерированные"')
    def mark_comments_moderated(self, request, queryset):
        updated_count = queryset.update(moderated=True)
        self.message_user(request, f'{updated_count} комментариев успешно помечены как "Модерированные".', level='success')
    actions = [mark_comments_moderated]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'text_preview', 'created_at', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'rating', 'created_at')
    search_fields = ('order__order_number', 'text')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('order',)

    def text_preview(self, obj):
        return obj.text[:75] + '...' if obj.text and len(obj.text) > 75 else (obj.text or '')
    text_preview.short_description = 'Текст отзыва'

    @admin.action(description='Опубликовать выбранные отзывы')
    def publish_reviews(self, request, queryset):
        updated_count = queryset.update(is_published=True)
        self.message_user(request, f'{updated_count} отзывов успешно опубликовано.', level='success')
    actions = [publish_reviews]