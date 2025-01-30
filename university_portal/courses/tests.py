from audioop import reverse
from datetime import time

from django.test import TestCase, Client
from users.models import User, UserLevel
from .models import Course, Department, Instructor, Enrollment, Student, Prerequisite, WeeklySchedule


class CourseListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name="Engineering")
        self.instructor = Instructor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department=self.department
        )
        Course.objects.create(
            name="Math 101",
            code="MTH101",
            credits=3,
            capacity=30,
            remaining_capacity=20,
            department=self.department,
            instructor=self.instructor
        )
        Course.objects.create(
            name="Physics 101",
            code="PHY101",
            credits=4,
            capacity=25,
            remaining_capacity=10,
            department=self.department,
            instructor=self.instructor
        )

    def test_get_all_courses(self):
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('courses')), 2)

    def test_filter_courses_by_department(self):
        response = self.client.get(f'/api/courses/?department_id={self.department.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('courses')), 2)

    def test_search_courses_by_name_or_code(self):
        response = self.client.get('/api/courses/?query=Math')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get('courses')), 1)


class AddCourseToEnrollmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a department
        self.department = Department.objects.create(name="Engineering")

        # Create a user level
        self.user_level = UserLevel.objects.create(name="Student")

        # Create a user
        self.user = User.objects.create(
            username="testuser",
            password="testpassword",
            user_level=self.user_level
        )

        # Create a student
        self.student = Student.objects.create(
            user=self.user,
            first_name="Test",
            last_name="Student",
            email="test@student.com",
            student_number="12345",
            admission_year=2023,
            max_units=20,
            year=1
        )

        # Create an instructor
        self.instructor = Instructor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department=self.department
        )

        # Create a course
        self.course = Course.objects.create(
            name="Math 101",
            code="MTH101",
            credits=3,
            capacity=30,
            remaining_capacity=10,
            department=self.department,
            instructor=self.instructor
        )

    def test_add_course_success(self):
        response = self.client.post('/api/courses/add/', {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Course added successfully', response.json().get('message'))

    def test_add_course_already_added(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        response = self.client.post('/api/courses/add/', {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Course already added', response.json().get('error'))

    def test_add_course_no_capacity(self):
        self.course.remaining_capacity = 0
        self.course.save()
        response = self.client.post('/api/courses/add/', {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Course is full', response.json().get('error'))


class DropCourseFromEnrollmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Setup data (similar to previous tests)
        self.department = Department.objects.create(name="Engineering")
        self.user_level = UserLevel.objects.create(name="Student")
        self.user = User.objects.create(username="testuser", password="testpassword", user_level=self.user_level)
        self.student = Student.objects.create(
            user=self.user, first_name="Test", last_name="Student", email="test@student.com", student_number="12345",
            admission_year=2023, max_units=20, year=1
        )
        self.instructor = Instructor.objects.create(first_name="John", last_name="Doe", email="john.doe@example.com", department=self.department)
        self.course = Course.objects.create(
            name="Math 101", code="MTH101", credits=3, capacity=30, remaining_capacity=29, department=self.department, instructor=self.instructor
        )
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course, status="Approved")

    def test_drop_course_success(self):
        response = self.client.post('/api/courses/drop/', {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Course dropped successfully', response.json().get('message'))

        # Reload the course to get updated remaining_capacity
        self.course.refresh_from_db()
        self.assertEqual(self.course.remaining_capacity, 30)  # Check updated capacity

    def test_drop_course_not_enrolled(self):
        Enrollment.objects.all().delete()  # Remove all enrollments
        response = self.client.post('/api/courses/drop/', {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn('Enrollment not found', response.json().get('error'))

    def test_drop_course_invalid_student(self):
        response = self.client.post('/api/courses/drop/', {
            'student_id': 999,  # Non-existent student
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn('Student not found', response.json().get('error'))


class CourseDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # تنظیم داده‌ها
        self.department = Department.objects.create(name="Engineering")
        self.instructor = Instructor.objects.create(
            first_name="John", last_name="Doe", email="john.doe@example.com", department=self.department
        )
        self.course = Course.objects.create(
            name="Math 101", code="MTH101", credits=3, capacity=30, remaining_capacity=25,
            department=self.department, instructor=self.instructor
        )
        self.prerequisite = Course.objects.create(
            name="Basic Math", code="BMTH101", credits=2, capacity=40, remaining_capacity=35,
            department=self.department, instructor=self.instructor
        )
        Prerequisite.objects.create(course=self.course, required_course=self.prerequisite)

    def test_course_detail_success(self):
        response = self.client.get(f'/api/courses/detail/{self.course.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('name'), 'Math 101')
        self.assertIn('Basic Math', response.json().get('prerequisites'))

    def test_course_detail_not_found(self):
        response = self.client.get('/api/courses/detail/999/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Course not found', response.json().get('error'))


class StudentEnrollmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create user level (Fix missing foreign key issue)
        self.user_level = UserLevel.objects.create(name="Student")  # FIXED

        # Create department
        self.department = Department.objects.create(name="Engineering")

        # Create instructor
        self.instructor = Instructor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department=self.department
        )

        # Create user for student with valid user_level
        self.user = User.objects.create(
            username="teststudent",
            password="password123",
            user_level=self.user_level  # FIXED: Assign the created user level
        )

        # Create student with a valid user_id
        self.student = Student.objects.create(
            first_name="Test",
            last_name="Student",
            email="test@student.com",
            student_number="12345",
            admission_year=2023,
            max_units=20,
            year=1,
            user=self.user  # Assign user to student
        )

        # Create prerequisite course (Assign capacity)
        self.prereq_course = Course.objects.create(
            name="Basic Math",
            code="BM101",
            credits=3,
            department=self.department,
            instructor=self.instructor,
            capacity=30,  # Assign capacity
            remaining_capacity=30  # Assign remaining capacity
        )

        # Create main course with prerequisite (Assign capacity)
        self.main_course = Course.objects.create(
            name="Advanced Math",
            code="AM201",
            credits=4,
            department=self.department,
            instructor=self.instructor,
            capacity=30,  # Assign capacity
            remaining_capacity=30  # Assign remaining capacity
        )

        Prerequisite.objects.create(course=self.main_course, required_course=self.prereq_course)

    def test_enroll_without_passing_prerequisite(self):
        response = self.client.post('/api/courses/enroll/', {
            'student_id': self.student.id,
            'course_id': self.main_course.id
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Prerequisite not completed', response.json().get('error'))

    def test_enroll_after_passing_prerequisite(self):
        # Mark prerequisite course as completed
        Enrollment.objects.create(student=self.student, course=self.prereq_course)

        response = self.client.post('/api/courses/enroll/', {
            'student_id': self.student.id,
            'course_id': self.main_course.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Enrollment successful', response.json().get('message'))


class AdminAddCourseTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.department = Department.objects.create(name="Engineering")
        self.instructor = Instructor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department=self.department
        )

    def test_add_course_successfully(self):
        response = self.client.post('/api/courses/admin/add-course/', {
            'name': 'Test Course',
            'code': 'TC101',
            'credits': 3,
            'instructor_id': self.instructor.id,
            'department_id': self.department.id,
            'capacity': 30,
            'remaining_capacity': 30  # ✅ FIXED: Set remaining_capacity
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Course added successfully', response.json().get('message'))


class AdminEditCourseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name="Engineering")
        self.instructor = Instructor.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            department=self.department
        )
        self.course = Course.objects.create(
            name="Old Course",
            code="OLD101",
            credits=3,
            instructor=self.instructor,
            department=self.department,
            capacity=30,
            remaining_capacity=30  # ✅ FIXED: Set remaining_capacity
        )

    def test_edit_course_successfully(self):
        response = self.client.post(f'/api/courses/admin/edit-course/{self.course.id}/', {
            'name': 'Updated Course',
            'code': 'NEW101',
            'credits': 4
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('Course updated successfully', response.json().get('message'))









