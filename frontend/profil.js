const themeToggle = document.getElementById('theme-toggle');

themeToggle.addEventListener('change', () => {
    const isDarkTheme = themeToggle.checked;
            
    document.body.classList.toggle('dark', isDarkTheme);
    document.body.classList.toggle('light', !isDarkTheme);

    const rectangle = document.querySelector('.rectangle');
    rectangle.classList.toggle('dark', isDarkTheme);
    rectangle.classList.toggle('light', !isDarkTheme);
            
    // Смена классов для текста
    const rectangle1 = document.querySelector('.rectangle1');
    rectangle1.classList.toggle('dark', isDarkTheme);
    rectangle1.classList.toggle('light', !isDarkTheme);

    const rectangle2 = document.querySelector('.rectangle2');
    rectangle2.classList.toggle('dark', isDarkTheme);
    rectangle2.classList.toggle('light', !isDarkTheme);

    const rectangle3 = document.querySelector('.rectangle3');
    rectangle3.classList.toggle('dark', isDarkTheme);
    rectangle3.classList.toggle('light', !isDarkTheme);
            
    const rectangle4 = document.querySelector('.rectangle4');
    rectangle4.classList.toggle('dark', isDarkTheme);
    rectangle4.classList.toggle('light', !isDarkTheme);

    const statisyica = document.querySelector('.statisyica');
    statisyica.classList.toggle('dark', isDarkTheme);
    statisyica.classList.toggle('light', !isDarkTheme);

    const kuplenno = document.querySelector('.kuplenno');
    kuplenno.classList.toggle('dark', isDarkTheme);
    kuplenno.classList.toggle('light', !isDarkTheme);

    const poprobavano = document.querySelector('.poprobavano');
    poprobavano.classList.toggle('dark', isDarkTheme);
    poprobavano.classList.toggle('light', !isDarkTheme);

    const popular = document.querySelector('.popular');
    popular.classList.toggle('dark', isDarkTheme);
    popular.classList.toggle('light', !isDarkTheme);

    const name = document.querySelector('.name');
    name.classList.toggle('dark', isDarkTheme);
    name.classList.toggle('light', !isDarkTheme);

    const burgerline = document.querySelector('.burgerline');
    burgerline.classList.toggle('dark', isDarkTheme);
    burgerline.classList.toggle('light', !isDarkTheme);

    const burgerline1 = document.querySelector('.burgerline1');
    burgerline1.classList.toggle('dark', isDarkTheme);
    burgerline1.classList.toggle('light', !isDarkTheme);

    const burgerline2 = document.querySelector('.burgerline2');
    burgerline2.classList.toggle('dark', isDarkTheme);
    burgerline2.classList.toggle('light', !isDarkTheme);

    const redactor = document.querySelector('.redactor');
    redactor.classList.toggle('dark', isDarkTheme);
    redactor.classList.toggle('light', !isDarkTheme);

    const karta = document.querySelector('.karta');
    karta.classList.toggle('dark', isDarkTheme);
    karta.classList.toggle('light', !isDarkTheme);
})

    // Установка начального состояния темы
themeToggle.checked = false; // Убедитесь, что тумблер выключен по умолчанию
document.querySelector('.submit-button').addEventListener("click", function(e) {
    e.preventDefault();
    window.location.href = "index.html"; // Укажите URL, на который нужно перейти
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