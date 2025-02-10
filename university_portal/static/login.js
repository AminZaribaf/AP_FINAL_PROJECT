
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();

        // دریافت نام کاربری و پسورد از فرم
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        console.log("Username entered:", username);
        console.log("Password entered:", password);        // گرفتن CSRF Token از کوکی
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

        const csrftoken = getCookie('csrftoken');

        // ارسال درخواست به سرور
        fetch('/api/users/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(response => response.json())
        .then(data => {
            // نمایش پیام موفقیت یا خطا
            if (data.message) {
                document.getElementById('success-message').style.display = 'block';
                document.getElementById('error-message').style.display = 'none';
                window.location.href = '/api/courses/';  // مسیر به داشبورد یا صفحه دیگر
            } else {
                document.getElementById('error-message').innerText = data.error || 'خطا در ورود! لطفاً دوباره تلاش کنید.';
                document.getElementById('error-message').style.display = 'block';
                document.getElementById('success-message').style.display = 'none';
            }
        })
        .catch(error => {
            document.getElementById('error-message').style.display = 'block';
            document.getElementById('success-message').style.display = 'none';
            console.error('Error:', error);
        });
    });
});
