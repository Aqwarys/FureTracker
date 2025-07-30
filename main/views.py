from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from consultations.forms import ConsultationRequestForm


# Ваше представление index
def index(request):
    form = ConsultationRequestForm()
    return render(request, 'main/index.html', {'form': form})

@require_http_methods(["POST"])
def consultation_submit_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ConsultationRequestForm(request.POST)

        if form.is_valid():
            consultation_instance = form.save()

            print(f"Новая AJAX заявка успешно сохранена:\nИмя: {consultation_instance.name}\nТелефон: {consultation_instance.phone}\nEmail: {consultation_instance.email if hasattr(consultation_instance, 'email') else 'N/A'}\nСообщение: {consultation_instance.message}")

            return JsonResponse({'status': 'success', 'message': 'Ваша заявка успешно отправлена!'})
        else:
            print("Ошибки валидации формы:", form.errors)
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': 'Пожалуйста, проверьте правильность введенных данных.', 'errors': errors}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Неверный тип запроса.'}, status=400)