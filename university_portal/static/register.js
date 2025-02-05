document.getElementById('registrationForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var errorMessages = [];

    var firstName = document.getElementById('firstName').value;
    var lastName = document.getElementById('lastName').value;
    var idNumber = document.getElementById('idNumber').value;
    var userCode = document.getElementById('userCode').value;
    var email = document.getElementById('email').value;
    var phone = document.getElementById('phone').value;
    var role = document.getElementById('role').value;

    // اعتبارسنجی ورودی‌ها
    if (firstName === "" || lastName === "") {
        errorMessages.push("لطفا نام و نام خانوادگی را وارد کنید.");
    }

    if (!/^\d{10}$/.test(idNumber)) {
        errorMessages.push("شماره ملی باید 10 رقم باشد.");
    }

    if (userCode === "") {
        errorMessages.push("کد دلخواه (نام کاربری) الزامی است.");
    }

    if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
        errorMessages.push("فرمت ایمیل معتبر نیست.");
    }

    if (!/^(?:\+98|0)?9\d{9}$/.test(phone)) {
        errorMessages.push("فرمت شماره تلفن معتبر نیست.");
    }

    if (errorMessages.length > 0) {
        document.getElementById('errorMessages').innerHTML = errorMessages.join('<br>');
    } else {
        document.getElementById('errorMessages').innerHTML = "";

        // ارسال داده‌ها به سرور با استفاده از Fetch API
        const formData = new FormData();
        formData.append('first_name', firstName);
        formData.append('last_name', lastName);
        formData.append('id_number', idNumber);
        formData.append('user_code', userCode);
        formData.append('email', email);
        formData.append('phone', phone);
        formData.append('role', role);

        fetch("/register/", {  // اطمینان حاصل کنید که مسیر `/register/` صحیح است
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())  // تبدیل پاسخ به JSON
        .then(data => {
            // در اینجا داده‌های موفقیت‌آمیز یا خطا بررسی می‌شوند
            if (data.success) {
                window.location.href = "/login/";  // انتقال به صفحه ورود در صورت موفقیت
            } else {
                document.getElementById('errorMessages').innerHTML = "خطا در ثبت‌نام: " + data.error; // نمایش خطا
            }
        })
        .catch(error => {
            console.error("Error:", error); // نمایش خطا در صورت بروز مشکل
        });
    }
});