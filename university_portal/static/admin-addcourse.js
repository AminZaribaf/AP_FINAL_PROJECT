
document.getElementById('addCourseForm').addEventListener('submit', function (e) {
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
        course_name: document.getElementById('courseName').value,
        course_code: document.getElementById('courseCode').value,
        department_id: document.getElementById('department').value,
        instructor_id: document.getElementById('instructor').value,
        credits: document.getElementById('credits').value,
        remaining_capacity: document.getElementById('remaining_capacity').value,
        capacity: document.getElementById('capacity').value,
        class_time: document.getElementById('classTime').value,
        exam_time: document.getElementById('examTime').value
    };

    fetch('/api/courses/admin/add-course', {
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
        alert('درس با موفقیت افزوده شد');
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
        alert('خطا در ارسال درخواست');
    });
});


