from django import forms
from consultations.models import ConsultationRequest

class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        fields = ['name', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Ваш телефон', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Опишите ваш запрос (необязательно)', 'rows': 4, 'class': 'form-control'}),
        }
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'message': 'Сообщение',
        }