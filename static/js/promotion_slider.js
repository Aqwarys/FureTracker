document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.promo-slide');
    const dots = document.querySelectorAll('.promo-dot');
    // const slider = document.querySelector('.promo-slider'); // Больше не нужен для transform

    if (!slides.length) {
        // Если акций нет, можно показать сообщение или скрыть секцию
        const promotionsSection = document.getElementById('promotions');
        if (promotionsSection) {
            promotionsSection.style.display = 'none'; // Скрываем всю секцию
        }
        return;
    }

    let index = 0;
    const total = slides.length;
    let interval; // Переменная для хранения интервала

    function updateSlider() {
        // УДАЛЕНО: slider.style.transform = `translateX(-${index * 100}%)`;

        slides.forEach((slide, i) => {
            if (i === index) {
                slide.classList.add('active'); // Активируем текущий слайд
            } else {
                slide.classList.remove('active'); // Деактивируем остальные слайды
            }
        });

        dots.forEach(dot => dot.classList.remove('active'));
        dots[index].classList.add('active');
    }

    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            clearInterval(interval); // Очищаем интервал при ручном переключении
            index = parseInt(dot.dataset.index);
            updateSlider();
            startAutoSlide(); // Запускаем интервал снова
        });
    });

    function startAutoSlide() {
        clearInterval(interval); // Убедимся, что предыдущий интервал остановлен
        interval = setInterval(() => {
            index = (index + 1) % total;
            updateSlider();
        }, 6000); // 6 секунд для автоматического переключения
    }

    // Инициализация и запуск слайдера
    updateSlider();
    startAutoSlide();
});
