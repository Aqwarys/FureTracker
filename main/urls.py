from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('consultation/submit/', views.consultation_submit_view, name='consultation_submit'),
]