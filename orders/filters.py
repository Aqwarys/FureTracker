import django_filters
from django.utils.timezone import now, timedelta
from orders.models import Order

class OrderFilter(django_filters.FilterSet):
    COMPLETED = 'Завершен'

    status = django_filters.CharFilter(
        method='filter_status', label='Статус'
    )

    last_month = django_filters.BooleanFilter(
        method='filter_last_month', label='За последний месяц'
    )

    class Meta:
        model = Order
        fields = ['status', 'last_month', 'order_number']

    def filter_status(self, queryset, name, value):
        if not value:  # Если выбран "Все"
            return queryset
        if value == 'completed':
            return queryset.filter(order_status__name=self.COMPLETED)
        if value == 'in_progress':
            return queryset.exclude(order_status__name__in=['Отменен', self.COMPLETED])
        return queryset


    def filter_last_month(self, queryset, name, value):
        if value:
            month_ago = now() - timedelta(days=30)
            return queryset.filter(created_at__gte=month_ago)
        return queryset
