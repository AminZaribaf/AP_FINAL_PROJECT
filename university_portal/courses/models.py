from django.db import models
from users.models import Student

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Instructor(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    credits = models.IntegerField()
    class_time = models.CharField(max_length=50)
    exam_time = models.CharField(max_length=50)
    capacity = models.IntegerField()
    remaining_capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # Pending, Approved, etc.

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.name}"


class Prerequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="main_course")
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="required_course")
    def __str__(self):
        return f"{self.required_course.name} is a prerequisite for  {self.course.name}"


class CoRequisite(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="main_course_coreq")
    required_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="required_course_coreq")
    def __str__(self):
        return f"{self.required_course.name} is a corequisite for  {self.course.name}"


class WeeklySchedule(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=15)  # e.g., Monday, Tuesday
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __str__(self):
        return f"{self.course.name} for ({self.student.user.username})"


class Classroom(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CourseClassroom(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.name} in {self.classroom.name}"



