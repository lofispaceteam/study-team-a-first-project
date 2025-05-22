const API_URL = "http://localhost:8000";  // подставь сюда URL твоего бэкенда

// Функция для сохранения токенов в localStorage
function saveTokens(accessToken, refreshToken) {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

// Функция для получения токена из localStorage
function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

// Функция очистки токенов (при выходе)
function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

// --- Страница логина ---
if (document.getElementById("login-form")) {
  const form = document.getElementById("login-form");
  const errorDiv = document.getElementById("error");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    errorDiv.textContent = "";

    try {
      const res = await fetch(API_URL + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail  `Ошибка авторизации`);
      }

      const data = await res.json();

      saveTokens(data.access_token, data.refresh_token);

      // Перенаправляем на профиль
      window.location.href = "profile.html";
    } catch (err) {
      errorDiv.textContent = err.message;
    }
  });
}

// --- Страница профиля ---
if (document.getElementById("profile-info")) {
  const profileDiv = document.getElementById("profile-info");
  const logoutBtn = document.getElementById("logout-btn");

  async function fetchProfile() {
    const token = getAccessToken();
    if (!token) {
      alert("Пожалуйста, войдите в систему");
      window.location.href = "index.html";
      return;
    }

    try {
      const res = await fetch(API_URL + "/me", {
        headers: {
          Authorization: "Bearer " + token,
        },
      });

      if (res.status === 401) {
        // Токен невалиден или просрочен
        alert("Сессия истекла, выполните повторный вход");
        clearTokens();
        window.location.href = "index.html";
        return;
      }

      if (!res.ok) {
        throw new Error("Ошибка получения профиля");
      }

      const profile = await res.json();

      profileDiv.innerHTML = `
        <p><b>Имя:</b> ${profile.first_name}</p>
        <p><b>Фамилия:</b> ${profile.last_name}</p>
        <p><b>Email:</b> ${profile.email}</p>
        <p><b>Телефон:</b> ${profile.phone_number  `не указан`}</p>
        ${
          profile.photo_url
            ? '<img src="${profile.photo_url}" alt="Аватар" width="150" />'
            : "<p>Фото не загружено</p>"
        }
      `;
    } catch (err) {
      profileDiv.textContent = err.message;
    }
  }

  logoutBtn.addEventListener("click", async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      clearTokens();
      window.location.href = "index.html";
      return;
    }

    try {
      const res = await fetch(API_URL + "/logout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) {
        throw new Error("Ошибка при выходе");
      }

      clearTokens();
      window.location.href = "index.html";
    } catch (err) {
      alert(err.message);
    }
  });

  fetchProfile();
}
const form = document.getElementById('register-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
        const res = await fetch("http://localhost:8000", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (res.ok) {
            alert("Регистрация успешна! Перенаправление на вход...");
            window.location.href = "login.html";
        } else {
            const error = await res.json();
            alert("Ошибка: " + error.detail);
        }
    } catch (err) {
        console.error("Ошибка:", err);
        alert("Произошла ошибка при регистрации");
    }
});

fetch("http://localhost:8000/register", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    first_name: "Иван",
    last_name: "Иванов",
    email: "ivan@example.com",
    phone_number: "+71234567890",
    password: "пароль123",
    confirm_password: "пароль123"
  })
})
.then(async (response) => {
  if (response.ok) {
    alert("Регистрация успешна!");
    // Можно перенаправить на страницу входа
    window.location.href = "login.html";
  } else {
    const error = await response.json();
    alert("Ошибка регистрации: " + error.detail);
  }
})
.catch(err => {
  alert("Ошибка сети или сервера");
  console.error(err);
});

// login.js
document.querySelector('#login-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const email = document.querySelector('#email').value;
  const password = document.querySelector('#password').value;

  try {
    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();

      // Сохраняем токены в localStorage
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      // Переход на страницу профиля
      window.location.href = "pofil.html";
    } else {
      const error = await response.json();
      alert("Ошибка: " + error.detail);
    }
  } catch (err) {
    alert("Ошибка подключения к серверу");
    console.error(err);
  }
});