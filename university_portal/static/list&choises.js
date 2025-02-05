
const courses = [
    { code: 'ENG101', name: 'مقدمه‌ای بر مهندسی', credits: 3, faculty: 'computer', time: '10:00-12:00', exam: '15:00', instructor: 'دکتر احمدی', totalCapacity: 30, enrolled: 23, prerequisites: [], coRequisites: [] },
    { code: 'SCI201', name: 'فیزیک 1', credits: 4, faculty: 'mechanical', time: '8:00-10:00', exam: '10:00', instructor: 'دکتر رضایی', totalCapacity: 28, enrolled: 25, prerequisites: ['ENG101'], coRequisites: [] },
    { code: 'ART301', name: 'تاریخ هنر', credits: 2, faculty: 'electrical', time: '16:00-18:00', exam: '17:00', instructor: 'دکتر نوری', totalCapacity: 25, enrolled: 25, prerequisites: [], coRequisites: [] },
    { code: 'ENG102', name: 'ریاضیات مهندسی', credits: 4, faculty: 'computer', time: '12:00-14:00', exam: '14:00', instructor: 'دکتر صالحی', totalCapacity: 30, enrolled: 29, prerequisites: ['ENG101'], coRequisites: [] },
    { code: 'SCI202', name: 'شیمی عمومی', credits: 3, faculty: 'mechanical', time: '8:00-10:00', exam: '13:00', instructor: 'دکتر موسوی', totalCapacity: 30, enrolled: 20, prerequisites: [], coRequisites: [] }
];

let selectedCourses = [];
let totalCredits = 0;
const maxCredits = 18; // سقف واحد مجاز

function updateCourses() {
    const faculty = document.getElementById('faculty').value;
    const search = document.getElementById('search').value.toLowerCase();
    const filteredCourses = courses.filter(course => {
        return (faculty === '' || course.faculty === faculty) &&
               (course.name.toLowerCase().includes(search) || course.code.toLowerCase().includes(search));
    });
    displayCourses(filteredCourses);
}

function displayCourses(courses) {
    const courseList = document.getElementById('courseList');
    courseList.innerHTML = '';
    courses.forEach(course => {
        const courseItem = document.createElement('tr');
        const isSelected = isCourseSelected(course.code);
        courseItem.innerHTML = `
            <td>
                <button onclick="addCourse('${course.code}')" id="add-${course.code}" ${isSelected ? 'disabled' : ''}>افزودن</button>
                <button onclick="removeCourse('${course.code}')">حذف</button>
            </td>
            <td>${course.enrolled}/${course.totalCapacity}</td>
            <td>${course.instructor}</td>
            <td>${course.time}</td>
            <td>${course.exam}</td>
            <td>${course.credits}</td>
            <td>${course.name}</td>
            <td>${course.code}</td>
        `;
        courseList.appendChild(courseItem);
    });
}

function isCourseSelected(courseCode) {
    return selectedCourses.some(course => course.code === courseCode);
}

function getCSRFToken() {
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfElement) {
        return csrfElement.value;
    } else {
        console.error('CSRF token element not found');
        return null;
    }
}

function addCourse(courseCode) {
    const course = courses.find(course => course.code === courseCode);
    const studentId = 123;  // باید ID دانشجو باشد (مثلاً از اطلاعات کاربر که وارد سیستم شده است)

    // جلوگیری از انتخاب دوباره یک درس
    if (isCourseSelected(courseCode)) {
        showNotification('این درس قبلاً انتخاب شده است!');
        return;
    }

    // بررسی سقف واحد
    if (totalCredits + course.credits > maxCredits) {
        showNotification('مجموع واحدهای انتخابی بیشتر از سقف مجاز است!');
        return;
    }

    // بررسی ظرفیت
    if (course.enrolled >= course.totalCapacity) {
        showNotification('ظرفیت درس پر شده است!');
        return;
    }

    // بررسی پیشنیازها
    for (let prereq of course.prerequisites) {
        if (!selectedCourses.some(selected => selected.code === prereq)) {
            showNotification('پیشنیازهای درس رعایت نشده است!');
            return;
        }
    }

    // بررسی همنیازها
    for (let coReq of course.coRequisites) {
        if (!selectedCourses.some(selected => selected.code === coReq)) {
            showNotification('همنیازی‌های درس رعایت نشده است!');
            return;
        }
    }

    // ارسال درخواست AJAX به سرور برای افزودن درس
    fetch('add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // ارسال توکن CSRF برای جلوگیری از حملات CSRF
        },
        body: JSON.stringify({ student_id: studentId, course_id: course.id })  // ارسال اطلاعات به سرور
    })
    .then(response => response.json())  // انتظار پاسخ به صورت JSON
    .then(data => {
        if (data.message) {
            // اگر درخواست موفق بود
            selectedCourses.push(course);  // درس را به لیست انتخابی اضافه می‌کنیم
            totalCredits += course.credits;  // تعداد واحدها را به روز می‌کنیم
            updateSelectedInfo();  // بروزرسانی اطلاعات دروس انتخابی
            updateCourses();  // بروزرسانی لیست دروس
            showNotification('درس با موفقیت اضافه شد!');  // نمایش پیام موفقیت
        } else {
            showNotification(data.error);  // اگر خطایی رخ داد
        }
    })
    .catch(error => {
        showNotification('خطا در اضافه کردن درس!');
        console.error('Error:', error);
    });
}


function removeCourse(courseCode) {
    const course = courses.find(course => course.code === courseCode);
    const studentId = 123;  // باید ID دانشجو باشد (مثلاً از اطلاعات کاربر که وارد سیستم شده است)

    // ارسال درخواست AJAX به سرور برای حذف درس
    fetch('drop/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()  // ارسال توکن CSRF برای جلوگیری از حملات CSRF
        },
        body: JSON.stringify({ student_id: studentId, course_id: course.id })  // ارسال اطلاعات به سرور
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // اگر درخواست موفق بود
            const courseIndex = selectedCourses.findIndex(course => course.code === courseCode);
            if (courseIndex !== -1) {
                selectedCourses.splice(courseIndex, 1);  // حذف درس از لیست
                totalCredits -= course.credits;  // به‌روزرسانی تعداد واحدها
                updateSelectedInfo();  // بروزرسانی اطلاعات دروس انتخابی
                updateCourses();  // بروزرسانی لیست دروس
                showNotification(data.message);  // نمایش پیام موفقیت
            }
        } else {
            showNotification(data.error);  // نمایش پیام خطا
        }
    })
    .catch(error => {
        showNotification('خطا در حذف درس!');
        console.error('Error:', error);
    });
}
function getCSRFToken() {
    const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfElement) {
        return csrfElement.value;
    } else {
        console.error('CSRF token element not found');
        return null;
    }
}
function updateSelectedInfo() {
    document.getElementById('selectedCredits').textContent = totalCredits;
}

function searchCourses() {
    updateCourses();
}

function showNotification(message) {
    // نمایش پیام هشدار به کاربر
    const notification = document.createElement('div');
    notification.classList.add('notification');
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// بارگذاری اولیه
updateCourses();

function addCourseToSchedule(courseCode, day, time) {
    const course = courses.find(course => course.code === courseCode);  // فرض کنید اطلاعات درس را از آرایه courses می‌گیرید

    if (course) {
        // ایجاد کلید برای ذخیره در localStorage
        const cellId = day + "_" + time;

        // ذخیره اطلاعات درس در localStorage
        localStorage.setItem(cellId, course.name);  // ذخیره نام درس

        // نمایش درس در جدول برنامه هفتگی
        document.getElementById(cellId).innerText = course.name;

        showNotification('درس به برنامه هفتگی افزوده شد!');
    }
}
