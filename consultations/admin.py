# consultation/admin.py
from django.contrib import admin
from .models import ConsultationRequest

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'message_preview', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',) # Show newest requests first
    list_editable = ('is_processed',) # Allow quick toggle of processing status

    def message_preview(self, obj):
        return obj.message[:75] + '...' if obj.message and len(obj.message) > 75 else (obj.message or '')
    message_preview.short_description = 'Сообщение'

    @admin.action(description='Пометить выбранные заявки как "Обработанные"')
    def mark_as_processed(self, request, queryset):
        updated_count = queryset.update(is_processed=True)
        self.message_user(request, f'{updated_count} заявок успешно помечены как "Обработанные".', level='success')
    actions = [mark_as_processed]