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

    const name = document.querySelector('.name');
    name.classList.toggle('dark', isDarkTheme);
    name.classList.toggle('light', !isDarkTheme);

    const surname = document.querySelector('.surname');
    surname.classList.toggle('dark', isDarkTheme);
    surname.classList.toggle('light', !isDarkTheme);

    const email = document.querySelector('.email');
    email.classList.toggle('dark', isDarkTheme);
    email.classList.toggle('light', !isDarkTheme);

    const number = document.querySelector('.number');
    number.classList.toggle('dark', isDarkTheme);
    number.classList.toggle('light', !isDarkTheme);

    const password = document.querySelector('.password');
    password.classList.toggle('dark', isDarkTheme);
    password.classList.toggle('light', !isDarkTheme);

    const passwordd = document.querySelector('.passwordd');
    passwordd.classList.toggle('dark', isDarkTheme);
    passwordd.classList.toggle('light', !isDarkTheme);
});
// Установка начального состояния темы
themeToggle.checked = false; // Убедитесь, что тумблер выключен по умолчанию
// Обработчик для кнопки регистрации
document.querySelector('.submit-button').addEventListener('click', function (e) {
    e.preventDefault();
    window.location.href = 'index.html';
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
  
});
// Установка начального состояния темы
themeToggle.checked = false; // Убедитесь, что тумблер выключен по умолчанию