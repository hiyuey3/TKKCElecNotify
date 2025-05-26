document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const usernameField = document.getElementById("username");
    const passwordField = document.getElementById("password");
    const rememberMeCheckbox = document.getElementById("remember-me");
    const loginMessage = document.getElementById("login-message");
    const cancelButton = document.getElementById("cancel-auto-login");

    if (!loginForm || !usernameField || !passwordField || !rememberMeCheckbox || !loginMessage || !cancelButton) {
        console.error("未找到某些表单元素，请检查 HTML 代码是否正确！");
        return;
    }

    let autoLoginTimeout = null;

    if (localStorage.getItem("rememberMe") === "true") {
        usernameField.value = localStorage.getItem("username") || "";
        passwordField.value = localStorage.getItem("password") || "";
        rememberMeCheckbox.checked = true;

        loginMessage.style.display = "block";

        autoLoginTimeout = setTimeout(() => {
            console.log("自动登录执行...");
            loginForm.submit();
        }, 1800);

        console.log("自动登录定时器 ID:", autoLoginTimeout);
    }

    cancelButton.addEventListener("click", function () {
        if (autoLoginTimeout) {
            clearTimeout(autoLoginTimeout);
            autoLoginTimeout = null;
            console.log("取消自动登录！");
        }
        loginMessage.style.display = "none";
    });

    loginForm.addEventListener("submit", function () {
        if (rememberMeCheckbox.checked) {
            localStorage.setItem("username", usernameField.value);
            localStorage.setItem("password", passwordField.value);
            localStorage.setItem("rememberMe", "true");
        } else {
            localStorage.removeItem("username");
            localStorage.removeItem("password");
            localStorage.setItem("rememberMe", "false");
        }
    });
});
