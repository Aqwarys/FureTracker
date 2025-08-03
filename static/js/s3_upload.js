// static/js/s3_upload.js

document.addEventListener('DOMContentLoaded', function() {
    // Получаем форму по её ID. Data-атрибуты будут читаться с неё.
    const s3UploadForm = document.getElementById('s3-upload-form');
    if (!s3UploadForm) {
        console.error("S3 upload form element not found. Make sure an element with id='s3-upload-form' exists.");
        return;
    }

    const fileInput = document.getElementById('id_media_file');
    const uploadButton = document.getElementById('upload-to-s3-btn');
    const orderStageSelect = document.getElementById('id_order_stage');
    const progressBarContainer = document.querySelector('.progress');
    const progressBar = document.getElementById('upload-progress-bar');
    const uploadStatusMessage = document.getElementById('upload-status-message');

    // Получаем значения из data-атрибутов формы
    const orderNumber = s3UploadForm.dataset.orderNumber;
    const s3GetPresignedUrl = s3UploadForm.dataset.presignedUrl;
    const s3CompleteUploadUrl = s3UploadForm.dataset.completeUploadUrl;

    // Убедимся, что все элементы существуют и данные были успешно получены
    if (!fileInput || !uploadButton || !orderStageSelect || !progressBar || !uploadStatusMessage || !orderNumber || !s3GetPresignedUrl || !s3CompleteUploadUrl) {
        console.error("Missing one or more required DOM elements or data attributes for S3 upload.");
        uploadStatusMessage.className = 'mt-2 text-danger';
        uploadStatusMessage.textContent = "Ошибка инициализации формы загрузки. Проверьте консоль разработчика.";
        return;
    }

    uploadButton.addEventListener('click', async () => {
        const file = fileInput.files[0];
        const selectedOrderStageId = orderStageSelect.value;

        if (!file) {
            uploadStatusMessage.className = 'mt-2 text-danger';
            uploadStatusMessage.textContent = 'Пожалуйста, выберите файл для загрузки.';
            return;
        }
        if (!selectedOrderStageId) {
            uploadStatusMessage.className = 'mt-2 text-danger';
            uploadStatusMessage.textContent = 'Пожалуйста, выберите этап заказа.';
            return;
        }

        uploadButton.disabled = true;
        fileInput.disabled = true;
        orderStageSelect.disabled = true;
        progressBarContainer.style.display = 'block';
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        uploadStatusMessage.className = 'mt-2 text-info';
        uploadStatusMessage.textContent = 'Подготовка к загрузке...';

        try {
            // 1. Запрос к Django для получения подписанного URL для S3
            const presignedResponse = await axios.post(s3GetPresignedUrl, {
                filename: file.name,
                filetype: file.type,
                order_number: orderNumber, // Передаем номер заказа
            }, {
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') // Функция для получения CSRF-токена
                }
            });

            const { presigned_url, file_path_on_s3 } = presignedResponse.data;

            // 2. Прямая загрузка файла на S3
            uploadStatusMessage.textContent = 'Загрузка файла на S3...';
            await axios.put(presigned_url, file, {
                headers: {
                    'Content-Type': file.type,
                },
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    progressBar.style.width = percentCompleted + '%';
                    progressBar.textContent = percentCompleted + '%';
                },
            });

            // 3. Уведомление Django об успешной загрузке на S3 и сохранение в базе
            uploadStatusMessage.textContent = 'Файл загружен. Сохранение данных в базу...';
            await axios.post(s3CompleteUploadUrl, {
                order_number: orderNumber,
                s3_file_path: file_path_on_s3,
                order_stage_id: selectedOrderStageId,
            }, {
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            uploadStatusMessage.className = 'mt-2 text-success';
            uploadStatusMessage.textContent = 'Файл успешно загружен и сохранен!';
            progressBar.style.width = '100%';
            progressBar.textContent = '100%';

            // Опционально: Очистить форму и перезагрузить страницу или только секцию медиа
            fileInput.value = ''; // Очищаем выбранный файл
            // Перезагрузка страницы, чтобы увидеть новый медиафайл:
            location.reload();

        } catch (error) {
            console.error('Ошибка загрузки медиа:', error);
            uploadStatusMessage.className = 'mt-2 text-danger';
            if (error.response && error.response.data && error.response.data.error) {
                uploadStatusMessage.textContent = `Ошибка: ${error.response.data.error}`;
            } else {
                uploadStatusMessage.textContent = 'Произошла ошибка при загрузке файла. Попробуйте еще раз.';
            }
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        } finally {
            uploadButton.disabled = false;
            fileInput.disabled = false;
            orderStageSelect.disabled = false;
        }
    });

    // Вспомогательная функция для получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});