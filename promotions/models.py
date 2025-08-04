from django.db import models

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок акции")
    description = models.TextField(verbose_name="Описание акции")
    banner_image = models.ImageField(upload_to='promotion_banners/', verbose_name="Изображение баннера")

    start_date = models.DateTimeField(verbose_name="Дата и время начала")
    end_date = models.DateTimeField(verbose_name="Дата и время окончания")

    is_active = models.BooleanField(default=True, verbose_name="Активна ли акция")
    order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего обновления")

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def is_currently_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date and self.is_active