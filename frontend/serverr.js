const API_URL = "http://localhost:8000";

// Функции для работы с токенами
function saveTokens(accessToken, refreshToken) {
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refreshToken);
}

function getAccessToken() {
  return localStorage.getItem("access_token");
}

function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

// Регистрация
if (document.getElementById("register-form")) {
  document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        alert("Регистрация успешна! Перенаправление на вход...");
        window.location.href = "login.html";
      } else {
        const error = await res.json();
        alert("Ошибка: " + (error.detail || "Неизвестная ошибка"));
      }
    } catch (err) {
      console.error("Ошибка:", err);
      alert("Произошла ошибка при регистрации");
    }
  });
}

// Логин
if (document.getElementById("login-form")) {
  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const errorDiv = document.getElementById("error");

    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Ошибка авторизации");
      }

      const data = await res.json();
      saveTokens(data.access_token, data.refresh_token);
      window.location.href = "profile.html";
    } catch (err) {
      errorDiv.textContent = err.message;
    }
  });
}

// Профиль
if (document.getElementById("profile-info")) {
  async function fetchProfile() {
    const token = getAccessToken();
    if (!token) {
      alert("Пожалуйста, войдите в систему");
      window.location.href = "login.html";
      return;
    }

    try {
      const res = await fetch(`${API_URL}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.status === 401) {
        alert("Сессия истекла, выполните повторный вход");
        clearTokens();
        window.location.href = "login.html";
        return;
      }

      if (!res.ok) throw new Error("Ошибка получения профиля");

      const profile = await res.json();
      document.getElementById("profile-info").innerHTML = `
        <p><b>Имя:</b> ${profile.first_name || "не указано"}</p>
        <p><b>Фамилия:</b> ${profile.last_name || "не указано"}</p>
        <p><b>Email:</b> ${profile.email}</p>
        <p><b>Телефон:</b> ${profile.phone_number || "не указан"}</p>
        ${profile.photo_url 
          ? `<img src="${profile.photo_url}" alt="Аватар" width="150" />` 
          : "<p>Фото не загружено</p>"
        }
      `;
    } catch (err) {
      console.error(err);
      document.getElementById("profile-info").textContent = err.message;
    }
  }

  document.getElementById("logout-btn").addEventListener("click", async () => {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      try {
        await fetch(`${API_URL}/logout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken })
        });
      } catch (err) {
        console.error("Ошибка при выходе:", err);
      }
    }
    clearTokens();
    window.location.href = "login.html";
  });

  fetchProfile();
}