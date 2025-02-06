from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from users.models import Student
from .models import Course, Enrollment, Prerequisite, CoRequisite, Department, Instructor, WeeklySchedule
from django.views import View
from .forms import AddCourseForm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminAddCourseSerializer, AddCourseResponseSerializer
from .models import Course, Instructor, Department

class CourseListView(View):
    def get(self, request):
        # Optional filters
        department_id = request.GET.get('department_id')  # Filter by department
        search_query = request.GET.get('query')  # Search by name or code

        # Fetch courses based on filters
        courses = Course.objects.all()
        if department_id:
            courses = courses.filter(department_id=department_id)
        if search_query:
            courses = courses.filter(name__icontains=search_query) | courses.filter(code__icontains=search_query)

        # Serialize courses
        course_list = list(courses.values('id', 'name', 'code', 'credits', 'capacity', 'remaining_capacity', 'department_id'))
        return JsonResponse({'courses': course_list}, safe=False)




# class AddCourseToEnrollmentView(View):
#     def post(self, request):
#         # Get data from request
#         student_id = request.POST.get('student_id')
#         course_id = request.POST.get('course_id')
#
#         # Validate student and course
#         try:
#             student = Student.objects.get(id=student_id)
#         except Student.DoesNotExist:
#             return JsonResponse({'error': 'Student not found'}, status=404)
#
#         try:
#             course = Course.objects.get(id=course_id)
#         except Course.DoesNotExist:
#             return JsonResponse({'error': 'Course not found'}, status=404)
#
#         # Check remaining capacity
#         if course.remaining_capacity <= 0:
#             return JsonResponse({'error': 'Course is full'}, status=400)
#
#         # Check if the course is already added
#         if Enrollment.objects.filter(student=student, course=course).exists():
#             return JsonResponse({'error': 'Course already added'}, status=400)
#
#         # Add course to enrollment
#         Enrollment.objects.create(student=student, course=course)
#         course.remaining_capacity -= 1
#         course.save()
#
#         return JsonResponse({'message': 'Course added successfully'})
import json
from django.http import JsonResponse
from django.views import View
from .models import Student, Course, Enrollment

class AddCourseToEnrollmentView(View):
    def post(self, request):
        # دریافت داده‌ها از درخواست
        data = json.loads(request.body)  # از request.body برای دریافت JSON استفاده می‌کنیم
        student_id = data.get('student_id')
        course_id = data.get('course_id')

        # اعتبارسنجی دانشجو
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        # اعتبارسنجی درس
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # بررسی ظرفیت باقی‌مانده
        if course.remaining_capacity <= 0:
            return JsonResponse({'error': 'Course is full'}, status=400)

        # بررسی اینکه آیا درس قبلاً اضافه شده است
        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'error': 'Course already added'}, status=400)

        # اضافه کردن درس به لیست دروس انتخابی دانشجو
        Enrollment.objects.create(student=student, course=course)
        course.remaining_capacity -= 1
        course.save()

        return JsonResponse({'message': 'Course added successfully'})


class DropCourseFromEnrollmentView(View):
    def post(self, request):
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        # Validate student
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        # Validate enrollment
        try:
            enrollment = Enrollment.objects.get(student=student, course_id=course_id)
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Enrollment not found'}, status=404)

        # Remove enrollment and update course capacity
        course = enrollment.course  # Get the course from the enrollment
        enrollment.delete()  # Delete the enrollment
        course.remaining_capacity += 1  # Increase the capacity
        course.save()  # Save the updated course

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
        student_id = request.GET.get('student_id')
        first_name = request.GET.get('first_name')
        phone_number = request.GET.get('phone_number')

        # بررسی ارسال شدن تمام مقادیر مورد نیاز
        if not student_id or not first_name or not phone_number:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        # جستجوی دانشجو با مشخصات داده شده
        try:
            student = Student.objects.get(id=student_id, first_name=first_name, phone_number=phone_number)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'No matching student found'}, status=404)

        # دریافت برنامه هفتگی دانشجو
        weekly_schedule = WeeklySchedule.objects.select_related('course').filter(student=student)

        # آماده‌سازی داده‌ها برای پاسخ
        schedule_data = [
            {
                'course': schedule.course.name,
                'day_of_week': schedule.day_of_week,
                'start_time': schedule.start_time.strftime('%H:%M') if schedule.start_time else None,
                'end_time': schedule.end_time.strftime('%H:%M') if schedule.end_time else None,
            }
            for schedule in weekly_schedule
        ]

        return JsonResponse({'schedule': schedule_data}, status=200)




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
    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        course.name = request.POST.get('name', course.name)
        course.code = request.POST.get('code', course.code)
        course.credits = int(request.POST.get('credits', course.credits))
        course.capacity = int(request.POST.get('capacity', course.capacity))

        instructor_id = request.POST.get('instructor_id')
        if instructor_id:
            try:
                course.instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return JsonResponse({'error': 'Instructor not found'}, status=404)

        department_id = request.POST.get('department_id')
        if department_id:
            try:
                course.department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({'error': 'Department not found'}, status=404)

        course.save()
        return JsonResponse({'message': 'Course updated successfully'})


# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .models import Course, Enrollment
from .forms import DeleteCourseForm



class AdminDeleteCourseView(View):
     def post(self, request, course_id):
         try:
             course = Course.objects.get(id=course_id)
         except Course.DoesNotExist:
             return JsonResponse({'error': 'Course not found'}, status=404)

         course.delete()
         return JsonResponse({'message': 'Course deleted successfully'})
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

