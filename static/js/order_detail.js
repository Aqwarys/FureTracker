document.addEventListener("DOMContentLoaded", function () {
    const progressBar = document.querySelector("#orderProgressBar");
    const fillLine = progressBar.querySelector(".progress-line-fill");
    const steps = Array.from(progressBar.querySelectorAll(".progress-step"));

    if (!progressBar || steps.length === 0) return;

    // Определяем последний "completed" или "current"
    let activeIndex = steps.findIndex(step => step.classList.contains("current"));
    if (activeIndex === -1) {
        activeIndex = steps.filter(step => step.classList.contains("completed")).length - 1;
    }

    // Рассчитываем ширину заполнения
    const totalSteps = steps.length - 1;
    let fillWidth = (activeIndex / totalSteps) * 100;
    fillWidth = Math.max(fillWidth, 0); // На случай если нет активных шагов

    // Анимация прогресс-бара
    requestAnimationFrame(() => {
        fillLine.style.width = fillWidth + "%";
    });

    // Добавляем активные классы для completed
    steps.forEach((step, index) => {
        if (index < activeIndex) {
            step.classList.add("completed");
        }
    });

    // Hover эффект для отображения имени статуса
    steps.forEach(step => {
        step.addEventListener("mouseenter", () => step.classList.add("hover"));
        step.addEventListener("mouseleave", () => step.classList.remove("hover"));
    });
});
