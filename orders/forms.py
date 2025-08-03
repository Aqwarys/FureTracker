from django import forms
from orders.models import Review, Comment, OrderMedia
from core.models import OrderStatus

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'placeholder': 'Поделитесь своими впечатлениями о заказе', 'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'rating': 'Ваша оценка',
            'text': 'Текст отзыва',
        }

class CommentForm(forms.ModelForm):
    # author_name будет автоматически заполняться из данных заказа
    # Мы не включаем его в форму здесь, но обработаем в view
    class Meta:
        model = Comment
        fields = ['author_name', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-control'}),
            'text': forms.Textarea(attrs={'placeholder': 'Напишите ваш комментарий', 'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'author_name': 'Ваше имя',
            'text': 'Комментарий',
        }

class OrderTrackingForm(forms.Form): # Это не ModelForm, так как она не сохраняет данные напрямую
    order_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите номер заказа', 'class': 'form-control'}),
        label='Номер заказа'
    )


class OrderMediaForm(forms.ModelForm):
    # order_stage уже есть в модели OrderMedia, но нам нужно предоставить его здесь
    # чтобы пользователь мог выбрать этап, к которому относится медиа.
    # exclude позволяет не отображать поле 'file', так как оно будет обрабатываться JS
    # order_id также будет передаваться JS, а не через форму
    class Meta:
        model = OrderMedia
        # Исключаем 'file' и 'order', так как они будут добавлены программно или через JS
        fields = ['order_stage']
        widgets = {
            'order_stage': forms.Select(attrs={'class': 'form-select mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_stage'].empty_label = 'Выберите этап заказа'
        self.fields['order_stage'].queryset = OrderStatus.objects.exclude(name='Отменен').order_by('order_index')
