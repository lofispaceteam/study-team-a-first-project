const themeToggle = document.getElementById('theme-toggle');

themeToggle.addEventListener('change', () => {
    const isDarkTheme = themeToggle.checked;

    document.body.classList.toggle('dark', isDarkTheme);
    document.body.classList.toggle('light', !isDarkTheme);

    const rectangle = document.querySelector('.rectangle');
    rectangle.classList.toggle('dark', isDarkTheme);
    rectangle.classList.toggle('light', !isDarkTheme);

    // Смена классов для текста
    const text = document.querySelector('.text');
    text.classList.toggle('dark', isDarkTheme);
    text.classList.toggle('light', !isDarkTheme);

    const pochta = document.querySelector('.pochta');
    pochta.classList.toggle('dark', isDarkTheme);
    pochta.classList.toggle('light', !isDarkTheme);

    const parol = document.querySelector('.parol');
    parol.classList.toggle('dark', isDarkTheme);
    parol.classList.toggle('light', !isDarkTheme);

    const zabil = document.querySelector('.zabil');
    zabil.classList.toggle('dark', isDarkTheme);
    zabil.classList.toggle('light', !isDarkTheme);

    const registr = document.querySelector('.registr');
    registr.classList.toggle('dark', isDarkTheme);
    registr.classList.toggle('light', !isDarkTheme);
});

// Установка начального состояния темы
themeToggle.checked = false; // Убедитесь, что тумблер выключен по умолчанию
// Обработчик для кнопки регистрации
document.querySelector('.registr').addEventListener('click', function (e) {
    e.preventDefault();
    window.location.href = 'registracia.html';
})
document.querySelector('.submit-button').addEventListener('click', function (e) {
    e.preventDefault();
    window.location.href = 'pofil.html';
});
// Функция переключения темы
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');

    if (isDark) {
        // Переключаем на светлую тему
        body.classList.remove('dark-theme');
        body.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    } else {
        // Переключаем на темную тему
        body.classList.add('dark-theme');
        body.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Проверка сохраненной темы при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    // Добавляем обработчик для переключателя
    document.getElementById('togggle').addEventListener('click', toggleTheme);
});