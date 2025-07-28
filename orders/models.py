# orders/models.py - UPDATED
import os
from django.db import models
from core.models import OrderStatus
import uuid

class Order(models.Model):
    client_name = models.CharField(max_length=100, blank=False, null=False)
    client_email = models.EmailField(max_length=100, blank=False, null=False)
    client_phone = models.CharField(max_length=100, blank=False, null=False)
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    description = models.TextField(blank=False, null=False)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.is_completed = (self.order_status.name == 'Завершен')

        if not self.id and not self.order_number:
            super().save(*args, **kwargs)
            self.order_number = f"ORD-{self.id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number or f"Заказ без номера ({self.id})"


def order_media_upload_to(instance, filename):
    # Эта функция формирует путь, который будет сохранен в базе данных
    # и который S3 StorageBackend будет использовать относительно 'location' (media/).
    # Результат: orders/ORD-000011/ваш_файл.mp4
    return os.path.join('orders', str(instance.order.order_number), filename)

class OrderMedia(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='media_items')
    # КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Используем динамическую функцию для upload_to
    file = models.FileField(upload_to=order_media_upload_to, blank=True, null=True)
    order_stage = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Медиа заказа'
        verbose_name_plural = 'Медиа заказов'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Медиа для заказа {self.order.order_number} на этапе {self.order_stage.name}"


class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    moderated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']


class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Оценка заказа от 1 до 5 звезд"
    )
    text = models.TextField(blank=True, null=True, help_text="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False, help_text="Опубликован ли отзыв (после модерации)")

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв к заказу {self.order.order_number} - {self.rating} звезд"
