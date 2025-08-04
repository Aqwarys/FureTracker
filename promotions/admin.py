from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'is_currently_active', 'order', 'created_at')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    ordering = ('order',)
    fields = ('title', 'description', 'banner_image', 'start_date', 'end_date', 'is_active', 'order')