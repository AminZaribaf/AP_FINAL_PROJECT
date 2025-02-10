let selectedCourses = [];
let totalUnits = 0;

document.addEventListener("DOMContentLoaded", function() {
    fetchDepartments();
    fetchCourses();
});

// Fetch departments for the department select dropdown
function fetchDepartments() {
    fetch('/api/departments/')
        .then(response => response.json())
        .then(data => {
            const departmentSelect = document.getElementById('department');
            data.departments.forEach(department => {
                const option = document.createElement('option');
                option.value = department.id;
                option.textContent = department.name;
                departmentSelect.appendChild(option);
            });
        });
}

// Fetch courses based on department and search query
function fetchCourses() {
    const departmentId = document.getElementById('department').value;
    const searchQuery = document.getElementById('search').value;

    const url = new URL('/api/courses/', window.location.origin);
    if (departmentId) url.searchParams.append('department_id', departmentId);
    if (searchQuery) url.searchParams.append('query', searchQuery);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);  // نمایش داده‌ها در کنسول برای بررسی
            displayCourses(data.courses);
        });
}

// Display courses in the table
function displayCourses(courses) {
    const courseTableBody = document.getElementById('courseTable').getElementsByTagName('tbody')[0];
    courseTableBody.innerHTML = '';  // Clear existing rows

    courses.forEach(course => {
        const row = document.createElement('tr');
        row.id = `course-${course.id}`;  // اضافه کردن id منحصر به فرد برای هر ردیف
        row.innerHTML = `
            <td>${course.code}</td>
            <td>${course.name}</td>
            <td>${course.credits}</td>
            <td>${course.capacity} (${course.capacity - course.remaining_capacity} taken)</td>
            <td>${course.class_time || 'N/A'}</td>
            <td>${course.exam_time || 'N/A'}</td>
            <td>${course.instructor_name || 'N/A'}</td>
            <td>
                <button class="add" onclick="addCourse(${course.id}, '${course.code}', ${course.credits})">افزودن</button>
                <button class="remove" onclick="dropCourse(${course.id}, '${course.code}', ${course.credits})" style="display:none;">حذف</button>
            </td>
        `;
        courseTableBody.appendChild(row);
    });
}

// Add course to the enrollment
// Add course to the enrollment
// Add course to the enrollment
function addCourse(courseId, courseCode, credits) {
    const studentId = document.querySelector('meta[name="student-id"]').getAttribute('content');  // یا از روش داده `data` استفاده کن
    console.log("Student ID:", studentId);  // بررسی اینکه آیا student_id درست دریافت می‌شود

    const requestData = {
        student_id: studentId,
        course_id: courseId
    };

    console.log("Sending data:", requestData);  // اضافه کردن این خط برای بررسی داده‌ها

    fetch('/api/courses/add/', {
        method: 'POST',
        headers: addCsrfHeader({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(requestData)  // ارسال داده‌ها به صورت JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Course added successfully') {
            selectedCourses.push({ id: courseId, code: courseCode, credits: credits });
            totalUnits += credits;
            document.getElementById('totalUnits').textContent = `تعداد واحدهای انتخاب‌شده: ${totalUnits}`;

            // Change the "add" button to "remove" for the current course
            const row = document.getElementById(`course-${courseId}`);
            const addButton = row.querySelector('.add');
            const removeButton = row.querySelector('.remove');
            addButton.style.display = 'none';
            removeButton.style.display = 'inline-block';

            alert('درس افزوده شد');
        } else {
            alert(data.error);
        }
    });
}

// Drop course from the enrollment
// Drop course from the enrollment
function dropCourse(courseId, courseCode, credits) {
    const studentId = document.querySelector('meta[name="student-id"]').getAttribute('content');  // یا از روش داده `data` استفاده کن

    // بررسی داده‌های ارسالی در کنسول
    console.log("Sending data for course drop:", { student_id: studentId, course_id: courseId });

    fetch('/api/courses/drop/', {
        method: 'POST',
        headers: addCsrfHeader({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify({
            student_id: studentId,
            course_id: courseId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Course dropped successfully') {
            selectedCourses = selectedCourses.filter(course => course.id !== courseId);
            totalUnits -= credits;
            document.getElementById('totalUnits').textContent = `تعداد واحدهای انتخاب‌شده: ${totalUnits}`;

            // Change the "remove" button to "add" for the current course
            const row = document.getElementById(`course-${courseId}`);
            const addButton = row.querySelector('.add');
            const removeButton = row.querySelector('.remove');
            addButton.style.display = 'inline-block';
            removeButton.style.display = 'none';

            alert('درس حذف شد');
        } else {
            alert(data.error);
        }
    });
}


// Function to get CSRF token from meta tag
function getCsrfToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}

// Add CSRF token to fetch headers
function addCsrfHeader(headers) {
    const csrfToken = getCsrfToken();
    if (!headers) {
        headers = {};
    }
    headers['X-CSRFToken'] = csrfToken;
    return headers;
}
