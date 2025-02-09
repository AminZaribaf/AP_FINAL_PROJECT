document.getElementById('registerForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // گرفتن CSRF Token از کوکی
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

    const csrftoken = getCookie('csrftoken'); // گرفتن CSRF Token

    const formData = {
         username: document.getElementById('username').value,
         password: document.getElementById('password').value,
         user_level_id: document.getElementById('user_level_id').value, // فقط شناسه user_level ارسال می‌شود
          first_name: document.getElementById('first_name').value,
           last_name: document.getElementById('last_name').value,
           email: document.getElementById('email').value,
          national_id: document.getElementById('national_id').value,
          phone_number: document.getElementById('phone_number').value,
          major: document.getElementById('major').value,
          year: document.getElementById('year').value,
          max_units: document.getElementById('max_units').value,
         student_number: document.getElementById('student_number').value,
         admission_year: document.getElementById('admission_year').value
     };


    fetch('/api/users/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken  // اضافه کردن CSRF Token به هدر
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error('Server returned error: ' + JSON.stringify(errData));
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        console.log('Student Number:', formData.student_number)
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});



