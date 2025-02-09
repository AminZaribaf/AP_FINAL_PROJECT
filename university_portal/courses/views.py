
from users.models import  User
from .models import  Prerequisite, CoRequisite
from .forms import AddCourseForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminAddCourseSerializer, AddCourseResponseSerializer
import json
from .models import  Student
from .models import Department, Instructor
from .models import  Enrollment

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import Course




class CourseListView(View):
    def get(self, request):
        department_id = request.GET.get('department_id')
        search_query = request.GET.get('query')

        courses = Course.objects.all()
        if department_id:
            courses = courses.filter(department_id=department_id)
        if search_query:
            courses = courses.filter(name__icontains=search_query) | courses.filter(code__icontains=search_query)

        departments = Department.objects.all()

        courses_with_enrollment = []
        for course in courses:
            enrolled_students = course.capacity - course.remaining_capacity
            courses_with_enrollment.append({
                'course': course,
                'enrolled_students': enrolled_students,
            })

        # دریافت شناسه دانشجوی لاگین‌شده از session
        student_id = request.session.get('user_id')

        return render(request, 'list&choises.html', {
            'courses_with_enrollment': courses_with_enrollment,
            'departments': departments,
            'department_id': department_id,
            'search_query': search_query,
            'student_id': student_id  # ارسال شناسه دانشجویی به HTML
        })






class AddCourseToEnrollmentView(View):
    def post(self, request):
        # ابتدا بررسی می‌کنیم که کاربر در سشن لاگین کرده باشد
        if 'user_id' not in request.session:
            return JsonResponse({'error': 'Not authenticated'}, status=401)

        # واکشی شیء user و سپس student مربوطه
        try:
            user = User.objects.get(id=request.session['user_id'])
            student = Student.objects.get(user=user)
        except (User.DoesNotExist, Student.DoesNotExist):
            return JsonResponse({'error': 'Student not found'}, status=404)

        # خواندن داده‌ها از request.body که به صورت JSON ارسال شده است
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
            student_id = data.get('student_id')  # اگر نیاز به student_id دارید
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        print("Course ID received:", course_id)  # چاپ برای بررسی

        if not course_id:
            return JsonResponse({'error': 'course_id is required'}, status=400)

        # واکشی درس
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # بررسی ظرفیت باقیمانده
        if course.remaining_capacity <= 0:
            return JsonResponse({'error': 'Course is full'}, status=400)

        # بررسی اینکه آیا از قبل انتخاب نشده است
        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'error': 'Course already added'}, status=400)

        # ایجاد رکورد انتخاب واحد
        Enrollment.objects.create(student=student, course=course)

        # کاهش ظرفیت
        course.remaining_capacity -= 1
        course.save()

        return JsonResponse({'message': 'Course added successfully'}, status=200)





class DropCourseFromEnrollmentView(View):
    def post(self, request):
        # ابتدا بررسی می‌کنیم که کاربر در سشن لاگین کرده باشد
        if 'user_id' not in request.session:
            return JsonResponse({'error': 'Not authenticated'}, status=401)

        # واکشی شیء user و سپس student مربوطه
        try:
            user = User.objects.get(id=request.session['user_id'])
            student = Student.objects.get(user=user)
        except (User.DoesNotExist, Student.DoesNotExist):
            return JsonResponse({'error': 'Student not found'}, status=404)

        # دریافت آیدی درس از فرم (POST)
        try:
            data = json.loads(request.body)
            course_id = data.get('course_id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not course_id:
            return JsonResponse({'error': 'course_id is required'}, status=400)

        # بررسی اینکه چنین انتخابی وجود داشته باشد
        try:
            enrollment = Enrollment.objects.get(student=student, course_id=course_id)
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Enrollment not found'}, status=404)

        # حذف رکورد انتخاب واحد و افزایش ظرفیت
        course = enrollment.course
        enrollment.delete()
        course.remaining_capacity += 1
        course.save()

        return JsonResponse({'message': 'Course dropped successfully'}, status=200)

class CourseDetailView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # اطلاعات پیش‌نیازها
        prerequisites = Prerequisite.objects.filter(course=course).values_list('required_course__name', flat=True)

        # داده‌های درس
        course_data = {
            'id': course.id,
            'name': course.name,
            'code': course.code,
            'credits': course.credits,
            'remaining_capacity': course.remaining_capacity,
            'department': course.department.name,
            'instructor': f"{course.instructor.first_name} {course.instructor.last_name}",
            'prerequisites': list(prerequisites),
        }

        return JsonResponse(course_data, status=200)


class StudentEnrollmentView(View):
    def post(self, request):
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        # Validate student
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        # Validate course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # Check if student is already enrolled in the course
        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'error': 'Student already enrolled in this course'}, status=400)

        # Check if student has completed all prerequisites
        prerequisites = Prerequisite.objects.filter(course=course).values_list('required_course_id', flat=True)
        passed_courses = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)

        for prereq in prerequisites:
            if prereq not in passed_courses:
                return JsonResponse({'error': 'Prerequisite not completed'}, status=400)

        # Check if course has corequisites and if they are being taken together
        corequisites = CoRequisite.objects.filter(course=course).values_list('required_course_id', flat=True)
        enrolled_courses = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)

        for coreq in corequisites:
            if coreq not in enrolled_courses:
                return JsonResponse({'error': 'Corequisite course must be taken together'}, status=400)

        # Check if student has enough remaining units
        total_enrolled_credits = sum(
            enrollment.course.credits for enrollment in Enrollment.objects.filter(student=student)
        )
        if total_enrolled_credits + course.credits > student.max_units:
            return JsonResponse({'error': 'Exceeds maximum units allowed for the student'}, status=400)

        # Check course capacity
        if course.remaining_capacity <= 0:
            return JsonResponse({'error': 'No remaining capacity for this course'}, status=400)

        # Enroll student
        Enrollment.objects.create(student=student, course=course, status="Pending")
        course.remaining_capacity -= 1
        course.save()

        return JsonResponse({'message': 'Enrollment successful'}, status=200)





class WeeklyScheduleView(View):
    def get(self, request):
        # بررسی لاگین بودن کاربر
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'Not authenticated'}, status=401)

        # واکشی Student
        try:
            user = User.objects.get(id=user_id)
            student = Student.objects.get(user=user)
        except (User.DoesNotExist, Student.DoesNotExist):
            return JsonResponse({'error': 'Student not found'}, status=404)

        # گرفتن لیست Enrollmentهای این دانشجو
        enrollments = Enrollment.objects.filter(student=student)

        # آماده‌سازی خروجی برای فرستادن به قالب و JSON
        schedule_data = []
        for enrollment in enrollments:
            course = enrollment.course
            try:
                parts = course.class_time.split()
                if len(parts) == 2:
                    day_of_week = parts[0]
                    start_end = parts[1].split('-')
                    if len(start_end) == 2:
                        start_time = start_end[0] if start_end[0] else None
                        end_time = start_end[1] if start_end[1] else None
                    else:
                        raise ValueError("Invalid time format")
                else:
                    raise ValueError("Invalid class_time format")
            except ValueError as e:
                print(f"Error parsing class_time for {course.name}: {e}")
                day_of_week, start_time, end_time = None, None, None

            schedule_data.append({
                'course': course.name,
                'code': course.code,
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time,
            })

        # بررسی اینکه آیا درخواست AJAX است یا خیر
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'schedule': schedule_data})

        # اگر درخواست معمولی است، قالب HTML را رندر کنید
        context = {
            'schedule_data': schedule_data
        }
        print("Schedule Data:", schedule_data)
        return render(request, 'schedules.html', context)


class AdminAddCourseView(APIView):
    def get(self, request):
        form = AddCourseForm()
        return render(request , "admin-addcourse.html" , {'form': form})
    def post(self, request):
        serializer = AdminAddCourseSerializer(data=request.data)
        if serializer.is_valid():
            course_name = serializer.validated_data['course_name']
            course_code = serializer.validated_data['course_code']
            instructor_id = serializer.validated_data['instructor_id']
            department_id = serializer.validated_data['department_id']
            credits = serializer.validated_data['credits']
            remaining_capacity = serializer.validated_data['remaining_capacity']
            capacity = serializer.validated_data['capacity']
            class_time = serializer.validated_data['class_time']
            exam_time = serializer.validated_data['exam_time']

            # ایجاد درس جدید
            instructor = Instructor.objects.get(id=instructor_id)
            department = Department.objects.get(id=department_id)

            course = Course.objects.create(
                name=course_name,
                code=course_code,
                credits=credits,
                instructor=instructor,
                department=department,
                capacity=capacity,
                remaining_capacity=remaining_capacity,
                class_time=class_time,
                exam_time=exam_time,
            )

            # بازگشت پاسخ موفقیت‌آمیز
            response_serializer = AddCourseResponseSerializer(course)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class AdminEditCourseView(View):
    def get(self, request, course_code=None):
        if course_code:
            try:
                # استفاده از course_code برای پیدا کردن دوره
                course = Course.objects.get(code=course_code)
                departments = Department.objects.all()
                instructors = Instructor.objects.all()
                return render(request, 'admin-editcourse.html', {
                    'course': course,
                    'departments': departments,
                    'instructors': instructors,
                })
            except Course.DoesNotExist:
                return JsonResponse({'error': 'Course not found'}, status=404)
        else:
            return render(request, 'admin-editcourse.html')

    def post(self, request, course_code):
        try:
            course = Course.objects.get(code=course_code)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # به‌روزرسانی اطلاعات دوره
        course.name = request.POST.get('name', course.name)
        course.code = request.POST.get('code', course.code)
        course.credits = int(request.POST.get('credits', course.credits))
        course.class_time = request.POST.get('class_time', course.class_time)
        course.exam_time = request.POST.get('exam_time', course.exam_time)
        course.capacity = int(request.POST.get('capacity', course.capacity))
        course.remaining_capacity = int(request.POST.get('remaining_capacity', course.remaining_capacity))

        # به‌روزرسانی مدرس
        instructor_id = request.POST.get('instructor_id')
        if instructor_id:
            try:
                course.instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return JsonResponse({'error': 'Instructor not found'}, status=404)

        # به‌روزرسانی دپارتمان
        department_id = request.POST.get('department_id')
        if department_id:
            try:
                course.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({'error': 'Department not found'}, status=404)

        # ذخیره تغییرات
        course.save()
        return JsonResponse({'message': 'Course updated successfully'})







class AdminDeleteCourseView(View):
    def get(self, request, course_code=None):
        if course_code:
            # اگر course_code در URL بود، درس را پیدا کرده و حذف کنید
            try:
                course = Course.objects.get(code=course_code)
                course.delete()
                return JsonResponse({'message': 'Course deleted successfully'})
            except Course.DoesNotExist:
                return JsonResponse({'error': 'Course not found'}, status=404)
        else:
            # اگر course_code در URL نبود، فقط فرم ورود کد درس نشان داده شود
            return render(request, 'admin-deletecourse.html')

    def post(self, request, course_code):
        try:
            course = Course.objects.get(code=course_code)
            course.delete()
            return JsonResponse({'message': 'Course deleted successfully'})
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)



class DepartmentCreateView(View):
    def post(self, request):
        department_name = request.POST.get('name')

        # بررسی اینکه دپارتمان از قبل وجود دارد یا نه
        if Department.objects.filter(name=department_name).exists():
            return JsonResponse({'error': 'Department already exists'}, status=400)

        # ایجاد دپارتمان جدید
        department = Department.objects.create(name=department_name)
        return JsonResponse({'message': 'Department created successfully', 'department_id': department.id})

class InstructorCreateView(View):
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        department_id = request.POST.get('department_id')

        if not first_name or not last_name or not email or not department_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'}, status=404)

        if Instructor.objects.filter(email=email, department=department).exists():
            return JsonResponse({'error': 'Instructor already exists in this department'}, status=400)

        instructor = Instructor.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=department
        )

        return JsonResponse({'message': 'Instructor created successfully', 'instructor_id': instructor.id}, status=201)

