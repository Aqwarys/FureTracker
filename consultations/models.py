from django.db import models

class ConsultationRequest(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    is_relevant = models.BooleanField(default=False, verbose_name='Актуально после консультации')
    consultant_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Консультант')



    class Meta:
        verbose_name = 'Заявка на консультацию'
        verbose_name_plural = 'Заявки на консультацию'
        ordering = ['-created_at']