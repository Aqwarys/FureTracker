from django.contrib import admin
from consultations.models import ConsultationRequest

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'message', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'phone', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_processed', 'mark_as_unprocessed']

    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
        self.message_user(request, "Выбранные заявки помечены как обработанные.")
    mark_as_processed.short_description = "Пометить как обработанные"

    def mark_as_unprocessed(self, request, queryset):
        queryset.update(is_processed=False)
        self.message_user(request, "Выбранные заявки помечены как необработанные.")
    mark_as_unprocessed.short_description = "Пометить как необработанные"