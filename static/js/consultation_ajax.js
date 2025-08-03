document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// AJAX обработка формы консультации (ОБНОВЛЕНО)
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('consultationForm');
    const submitButton = form.querySelector('button[type="submit"]');

    // Получаем ссылки на элементы модального окна
    const statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
    const modalTitle = document.getElementById('statusModalLabel');
    const modalIcon = document.getElementById('modalIcon');
    const modalMessage = document.getElementById('modalMessage');

    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // Предотвращаем стандартную отправку формы

            // Очищаем предыдущие сообщения и иконки
            modalTitle.textContent = 'Статус заявки';
            modalIcon.innerHTML = '';
            modalMessage.textContent = '';

            submitButton.disabled = true; // Отключаем кнопку
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Отправка...'; // Показываем спиннер

            const formData = new FormData(form);
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                const result = await response.json();

                if (response.ok) { // Если ответ 2xx (успех)
                    modalTitle.textContent = 'Успешно!';
                    modalIcon.innerHTML = '<i class="fas fa-check-circle text-success" style="font-size: 3rem;"></i>'; // Иконка успеха
                    modalMessage.textContent = result.message;
                    form.reset(); // Очищаем форму
                } else { // Если ответ 4xx, 5xx (ошибка)
                    modalTitle.textContent = 'Ошибка!';
                    modalIcon.innerHTML = '<i class="fas fa-times-circle text-danger" style="font-size: 3rem;"></i>'; // Иконка ошибки
                    modalMessage.textContent = result.message || 'Произошла ошибка при отправке заявки.';
                    // Если есть детальные ошибки, можно их вывести в модальном окне
                    if (result.errors) {
                        let errors = JSON.parse(result.errors);
                        for (const field in errors) {
                            errors[field].forEach(error => {
                                modalMessage.innerHTML += `<br><strong>${field}:</strong> ${error.message}`;
                            });
                        }
                    }
                }
            } catch (error) {
                console.error('Ошибка AJAX:', error);
                modalTitle.textContent = 'Ошибка сети!';
                modalIcon.innerHTML = '<i class="fas fa-exclamation-triangle text-warning" style="font-size: 3rem;"></i>'; // Иконка предупреждения
                modalMessage.textContent = 'Произошла ошибка сети или сервера. Пожалуйста, попробуйте еще раз.';
            } finally {
                submitButton.disabled = false; // Включаем кнопку обратно
                submitButton.innerHTML = 'Отправить заявку'; // Возвращаем исходный текст кнопки
                statusModal.show(); // Показываем модальное окно
            }
        });
    }
});
