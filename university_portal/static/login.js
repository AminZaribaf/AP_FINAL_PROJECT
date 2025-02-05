// let loginAttempts = 0;
//
// document.getElementById('loginForm').addEventListener('submit', function(event) {
//     event.preventDefault();
//
//     const studentId = document.getElementById('studentId').value;
//     const password = document.getElementById('password').value;
//
//     // داده‌های پیش‌فرض برای ورود (این اطلاعات باید از دیتابیس گرفته شوند)
//     const validCredentials = {
//         "student123": "password123", // شماره دانشجویی و کلمه عبور
//         "admin123": "adminpassword"  // برای ادمین
//     };
//
//     // بررسی ورودی‌های صحیح
//     if (validCredentials[studentId] && validCredentials[studentId] === password) {
//         // در صورت درست بودن ورود، انتقال به صفحه اصلی یا داشبورد
//         alert("ورود موفقیت‌آمیز بود!");
//         window.location.href = "dashboard.html";  // انتقال به صفحه داشبورد
//     } else {
//         loginAttempts++;
//         if (loginAttempts >= 3) {
//             // پس از 3 تلاش اشتباه، انتقال به صفحه مدیریت دروس و دانشجویان
//             alert("تلاش‌های ورود اشتباه به حد مجاز رسید. به صفحه مدیریت منتقل می‌شوید.");
//             window.location.href = "adminDashboard.html";  // صفحه مدیریت
//         } else {
//             document.getElementById('errorMessage').innerText = "شماره دانشجویی یا کلمه عبور اشتباه است.";
//         }
//     }
// });
document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const studentId = document.getElementById('studentId').value;
    const password = document.getElementById('password').value;

    // ارسال داده‌ها به سرور
    const formData = new FormData();
    formData.append('username', studentId);
    formData.append('password', password);

    fetch("/login/", {  // مطمئن شوید که مسیر `/login/` صحیح است
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // ورود موفقیت‌آمیز
            window.location.href = "dashboard.html";  // انتقال به صفحه داشبورد
        } else {
            // پیام خطا در صورت اشتباه بودن ورود
            document.getElementById('errorMessage').innerText = "شماره دانشجویی یا کلمه عبور اشتباه است.";
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});
