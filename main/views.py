from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from consultations.forms import ConsultationRequestForm
from promotions.models import Promotion
from core.models import FAQ
import logging

logger = logging.getLogger(__name__)


def index(request):
    logger.info("Запрос на главную страницу")
    promotions = Promotion.objects.filter(is_active=True).order_by('-order', '-created_at')
    logger.info("Получены активные промоакции")

    faqs = FAQ.objects.all().order_by('order')
    logger.info("Получены вопросы-ответы")
    form = ConsultationRequestForm()
    return render(request, 'main/index.html', {'form': form, 'promotions': promotions, 'faqs': faqs})

@require_http_methods(["POST"])
def consultation_submit_view(request):
    logger.info("Запрос на отправку заявки")
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.info("Запрос AJAX отправки заявки")
        form = ConsultationRequestForm(request.POST)

        if form.is_valid():
            logger.info("Заявка прошла валидацию")
            consultation_instance = form.save()
            logger.info(f"Новая AJAX заявка успешно сохранена:\nИмя: {consultation_instance.name}\nТелефон: {consultation_instance.phone}\nEmail: {consultation_instance.email if hasattr(consultation_instance, 'email') else 'N/A'}\nСообщение: {consultation_instance.message}")

            return JsonResponse({'status': 'success', 'message': 'Ваша заявка успешно отправлена!'})
        else:
            logger.info(f"Заявка не прошла валидацию:\n{form.errors.as_json()}")
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'Пожалуйста, проверьте правильность введенных данных.', 'errors': errors}, status=400)
    else:
        logger.info("Запрос не AJAX отправки заявки (неверный тип запроса) консультации")
        return JsonResponse({'status': 'error', 'message': 'Неверный тип запроса.'}, status=400)