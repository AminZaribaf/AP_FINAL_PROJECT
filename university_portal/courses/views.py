from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from users.models import Student
from .models import Course, Enrollment, Prerequisite


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


class AddCourseToEnrollmentView(View):
    def post(self, request):
        # Get data from request
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        # Validate student and course
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)

        # Check remaining capacity
        if course.remaining_capacity <= 0:
            return JsonResponse({'error': 'Course is full'}, status=400)

        # Check if the course is already added
        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'error': 'Course already added'}, status=400)

        # Add course to enrollment
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


class CourseListView(View):
    def get(self, request):
        # Get optional filters
        department_id = request.GET.get('department_id')
        search_query = request.GET.get('q')

        # Filter courses
        courses = Course.objects.all()

        if department_id:
            courses = courses.filter(department_id=department_id)

        if search_query:
            courses = courses.filter(name__icontains=search_query)

        # Serialize course data
        course_data = [
            {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'credits': course.credits,
                'remaining_capacity': course.remaining_capacity,
                'department': course.department.name
            }
            for course in courses
        ]

        return JsonResponse({'courses': course_data}, status=200)


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

        # Check course capacity
        if course.remaining_capacity <= 0:
            return JsonResponse({'error': 'No remaining capacity for this course'}, status=400)

        # Check if already enrolled
        if Enrollment.objects.filter(student=student, course=course).exists():
            return JsonResponse({'error': 'Student already enrolled in this course'}, status=400)

        # Check if student has enough remaining units
        total_enrolled_credits = sum(
            enrollment.course.credits for enrollment in Enrollment.objects.filter(student=student)
        )
        if total_enrolled_credits + course.credits > student.max_units:
            return JsonResponse({'error': 'Exceeds maximum units allowed for the student'}, status=400)

        # Enroll student
        Enrollment.objects.create(student=student, course=course, status="Pending")
        course.remaining_capacity -= 1
        course.save()

        return JsonResponse({'message': 'Enrollment successful'}, status=200)


class WeeklyScheduleView(View):
    @method_decorator(login_required)
    def get(self, request):
        try:
            # Ensure the user is associated with a Student profile
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student profile not found for this user'}, status=404)

        # Fetch the weekly schedule
        weekly_schedule = student.weeklyschedules.select_related('course').all()

        # Prepare the response data
        schedule_data = [
            {
                'course': schedule.course.name,
                'day_of_week': schedule.day_of_week,
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
            }
            for schedule in weekly_schedule
        ]

        return JsonResponse({'schedule': schedule_data}, status=200)




