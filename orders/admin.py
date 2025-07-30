# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html # For displaying HTML (thumbnails/previews)
from django.db.models import Count, Q # For aggregation (counting comments, media items)

# Import your models
from .models import Order, OrderMedia, Comment, Review
# Import OrderStatus from core app
from core.models import OrderStatus # Make sure this import path is correct for your project structure

# --- Global Admin Site Customization (Branding) ---
admin.site.site_header = "Панель управления Бизнесом"
admin.site.site_title = "Управление Заказами и Контентом"
admin.site.index_title = "Добро пожаловать в админ-панель"

# --- Inline Forms for Related Models ---
# OrderMediaInline: allows managing media files directly from the Order form
class OrderMediaInline(admin.TabularInline): # Use TabularInline for a compact table view
    model = OrderMedia
    extra = 1 # Number of empty forms to display for adding new media
    fields = ('order_stage', 'file', 'uploaded_at', 'get_thumbnail_or_preview')
    readonly_fields = ('uploaded_at', 'get_thumbnail_or_preview',)

    # Method to display a thumbnail for images or an icon for videos in the admin
    def get_thumbnail_or_preview(self, obj):
        if obj.file:
            file_url = obj.file.url
            file_ext = file_url.lower().split('.')[-1]
            if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                return format_html('<img src="{}" style="max-width: 100px; max-height: 100px; object-fit: contain; border-radius: 4px;" />', file_url)
            elif file_ext in ['mp4', 'mov', 'avi', 'webm']:
                # For videos, display a clear icon. You might need Font Awesome CDN in base.html for this to show.
                return format_html('<i class="fas fa-video fa-2x" style="color: #6c757d;" title="Видео файл"></i>')
        return format_html('<span style="color: #adb5bd;">Нет файла</span>')
    get_thumbnail_or_preview.short_description = 'Превью'


# CommentInline: allows managing comments directly from the Order form
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0 # Don't show empty forms by default
    fields = ('author_name', 'text', 'created_at', 'moderated')
    readonly_fields = ('created_at',)
    # Managers can directly toggle 'moderated' on the form


# ReviewInline: allows managing the review directly from the Order form
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    max_num = 1 # Only one review per order
    fields = ('rating', 'text', 'created_at', 'is_published')
    readonly_fields = ('created_at',)
    # Managers can directly toggle 'is_published' on the form


# --- Registering Models with Custom Admin Options ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Fields to display in the order list view
    list_display = (
        'order_number', 'order_status', 'client_name', 'client_phone',
        'is_completed', 'created_at', 'updated_at',
        'get_media_count', 'get_comments_count', 'has_review_status'
    )
    # Filters in the sidebar for the order list
    list_filter = ('order_status', 'is_completed', 'created_at')
    # Fields to search by
    search_fields = (
        'order_number', 'description', 'client_name', 'client_email', 'client_phone',
        'order_status__name' # Allows searching by status name
    )
    # Date hierarchy for easy navigation by year/month/day
    date_hierarchy = 'created_at'
    # Default ordering for the list
    ordering = ('-created_at',)
    # Show save buttons at the top of the form
    save_on_top = True
    # Number of items per page in the list view
    list_per_page = 25

    # Grouping fields on the add/change form for better organization
    fieldsets = (
        (None, {
            'fields': ('order_number', 'order_status', 'description'),
        }),
        ('Информация о клиенте', {
            'fields': ('client_name', 'client_email', 'client_phone'),
            'description': 'Контактные данные клиента для этого заказа.',
        }),
        ('Служебная информация', {
            'fields': ('access_token', 'is_completed', 'created_at', 'updated_at'),
            'classes': ('collapse',), # Make this section collapsible
            'description': 'Технические детали заказа, не предназначенные для частого редактирования.'
        }),
    )

    readonly_fields = ('order_number', 'access_token', 'is_completed', 'created_at', 'updated_at')

    # Including inline forms for related objects
    inlines = [OrderMediaInline, CommentInline, ReviewInline]

    # Annotate queryset for efficient counting in list_display
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Using `_count` suffix to avoid clashes if model has fields named 'media_count'
        queryset = queryset.annotate(
            _media_count=Count('media_items', distinct=True),
            _comments_count=Count('comments', distinct=True),
            _has_review=Count('review', distinct=True) # Count related review objects
        )
        return queryset

    # Custom methods for list_display
    def get_media_count(self, obj):
        return obj._media_count
    get_media_count.short_description = 'Медиа (шт.)'
    get_media_count.admin_order_field = '_media_count' # Allows sorting by this calculated field

    def get_comments_count(self, obj):
        return obj._comments_count
    get_comments_count.short_description = 'Комментарии (шт.)'
    get_comments_count.admin_order_field = '_comments_count'

    def has_review_status(self, obj):
        # Check if a review exists and if it's published or not
        if hasattr(obj, 'review'): # Check if a review object is related
            return obj.review.is_published
        return False
    has_review_status.boolean = True # Display as a checkbox
    has_review_status.short_description = 'Отзыв опубликован?'
    # Note: Can't easily sort by a boolean field that requires a relation lookup without more complex annotations.


    # Custom admin actions
    @admin.action(description='Пометить выбранные заказы как "Завершенные"')
    def mark_orders_completed(self, request, queryset):
        try:
            completed_status = OrderStatus.objects.get(name='Завершен')
            updated_count = queryset.update(order_status=completed_status)
            self.message_user(request, f'{updated_count} заказов успешно помечены как "Завершенные".', level='success')
        except OrderStatus.DoesNotExist:
            self.message_user(request, 'Статус "Завершен" не найден. Проверьте модель OrderStatus.', level='error')
    actions = [mark_orders_completed]

import os
@admin.register(OrderMedia)
class OrderMediaAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_stage', 'get_file_name', 'get_file_type', 'uploaded_at', 'get_thumbnail_or_preview_list')
    list_filter = ('order_stage', 'uploaded_at')
    search_fields = ('order__order_number', 'order_stage__name') # Search by order number and stage name
    autocomplete_fields = ('order',) # For efficient selection of an Order ForeignKey
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

    # Re-use the inline's preview method for list display
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
