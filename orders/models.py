from django.db import models
from core.models import OrderStatus
import uuid

class Order(models.Model):
    client_name = models.CharField(max_length=100, blank=False, null=False)
    client_email = models.EmailField(max_length=100, blank=False, null=False)
    client_phone = models.CharField(max_length=100, blank=False, null=False)
    access_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    order_number = models.CharField(max_length=100, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

class OrderMedia(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='media_items')
    file = models.FileField(upload_to='orders/media/', blank=True, null=True)
    order_stage = models.ForeignKey(OrderStatus, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Медиа заказа'
        verbose_name_plural = 'Медиа заказов'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Медиа для заказа {self.order.order_number} на этапе {self.order_stage.name}"


class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    moderated = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review') # OneToOne, так как обычно 1 заказ = 1 отзыв
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], # Оценка от 1 до 5
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