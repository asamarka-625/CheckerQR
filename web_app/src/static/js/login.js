document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById("loginForm");
    const btn = document.getElementById("loginBtn");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        errorLogin = document.getElementById("error_login");
        errorLogin.innerHTML = "";

        hideMessage();

        btn.disabled = true;
        btn.textContent = "Вход...";

        try {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            const response = await fetch(`/${PREFIX}/api/v1/auth/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error("Ошибка авторизации");
            }

            const data = await response.json();

            // сохраняем токен
            localStorage.setItem("token", data.access_token);

            showSuccess('Успешный вход');

            // редирект
            setTimeout(() => {
                window.location.href = `/${PREFIX}/events`;
            }, 500);

        } catch (e) {
            errorLogin.innerHTML = "<div class='error'>Неверный логин или пароль</div>";

        } finally {
            btn.disabled = false;
            btn.textContent = "Войти";
        }
    });
});