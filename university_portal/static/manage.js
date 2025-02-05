// داده‌های دروس نمونه
let courses = [
    { name: 'فیزیک 1', code: 'PHY101', faculty: 'دانشکده علوم', professor: 'دکتر احمدی', capacity: 30, enrolled: 25 },
    { name: 'ریاضیات 1', code: 'MATH101', faculty: 'دانشکده ریاضیات', professor: 'دکتر موسوی', capacity: 30, enrolled: 30 },
    { name: 'برنامه‌نویسی', code: 'CS101', faculty: 'دانشکده کامپیوتر', professor: 'دکتر کریمی', capacity: 40, enrolled: 15 },
];

// نمایش دروس در جدول
function renderCourses() {
    const coursesList = document.getElementById('coursesList');
    coursesList.innerHTML = ''; // پاک کردن محتوای قبلی

    courses.forEach(course => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${course.name}</td>
            <td>${course.code}</td>
            <td>${course.faculty}</td>
            <td>${course.professor}</td>
            <td>${course.capacity}</td>
            <td>
                <button onclick="editCourse('${course.code}')">ویرایش</button>
                <button onclick="deleteCourse('${course.code}')">حذف</button>
            </td>
        `;
        coursesList.appendChild(row);
    });
}

// ویرایش درس
function editCourse(courseCode) {
    const course = courses.find(c => c.code === courseCode);
    if (course) {
        alert(`ویرایش درس: ${course.name}`);
        // در اینجا فرم ویرایش نمایش داده می‌شود
    }
}

// حذف درس
function deleteCourse(courseCode) {
    courses = courses.filter(c => c.code !== courseCode);
    renderCourses();
}

// نمایش گزارش وضعیت دروس
function renderCourseChart() {
    const ctx = document.getElementById('courseChart').getContext('2d');
    const labels = courses.map(c => c.name);
    const data = courses.map(c => c.capacity - c.enrolled); // ظرفیت خالی

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'ظرفیت خالی دروس',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// نمایش دروس به محض بارگذاری صفحه
window.onload = function() {
    renderCourses();
    renderCourseChart();
};
