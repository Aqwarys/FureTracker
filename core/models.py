from django.db import models

class OrderStatus(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(unique=True, help_text='Порядковый номер для сортировки статусов')

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'
        ordering = ['order_index']

    def __str__(self):
        return self.name