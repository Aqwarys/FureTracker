from django.contrib import admin
from .models import ConsultationRequest

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'phone', 'message_preview', 'created_at',
        'is_processed', 'is_relevant', 'consultant_name'
    )
    list_filter = ('is_processed', 'is_relevant', 'created_at')
    search_fields = ('name', 'phone', 'message', 'consultant_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    list_editable = ('is_processed', 'is_relevant', 'consultant_name')

    def message_preview(self, obj):
        return obj.message[:75] + '...' if obj.message and len(obj.message) > 75 else (obj.message or '')
    message_preview.short_description = 'Сообщение'

    @admin.action(description='Пометить выбранные заявки как "Обработанные"')
    def mark_as_processed(self, request, queryset):
        updated_count = queryset.update(is_processed=True)
        self.message_user(request, f'{updated_count} заявок успешно помечены как "Обработанные".', level='success')

    @admin.action(description='Пометить выбранные заявки как "Актуальные"')
    def mark_as_relevant(self, request, queryset):
        updated_count = queryset.update(is_relevant=True)
        self.message_user(request, f'{updated_count} заявок успешно помечены как "Актуальные".', level='success')

    @admin.action(description='Пометить выбранные заявки как "Неактуальные"')
    def mark_as_irrelevant(self, request, queryset):
        updated_count = queryset.update(is_relevant=False)
        self.message_user(request, f'{updated_count} заявок успешно помечены как "Неактуальные".', level='success')

    actions = [
        mark_as_processed,
        mark_as_relevant,
        mark_as_irrelevant
    ]