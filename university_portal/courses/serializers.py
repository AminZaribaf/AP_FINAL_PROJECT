from rest_framework import serializers
from .models import Course, Instructor, Department


class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = ['id', 'name']  # فقط ID و نام استاد را نمایش می‌دهیم


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']  # فقط ID و نام دانشکده را نمایش می‌دهیم


class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()  # استاد مرتبط به درس
    department = DepartmentSerializer()  # دانشکده مرتبط به درس

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'credits', 'instructor', 'department', 'capacity', 'remaining_capacity',
                  'class_time', 'exam_time']

    # اگر بخواهید فقط ID استاد و دانشکده را ارسال کنید به جای استفاده از سریالایزرها می‌توانید از PrimaryKeyRelatedField استفاده کنید.
    # برای مثال:
    # instructor = serializers.PrimaryKeyRelatedField(queryset=Instructor.objects.all())
    # department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
class AdminAddCourseSerializer(serializers.Serializer):
    course_name = serializers.CharField(max_length=100)
    course_code = serializers.CharField(max_length=20)
    instructor_id = serializers.IntegerField()  # ID استاد
    department_id = serializers.IntegerField()  # ID دانشکده
    credits = serializers.IntegerField()
    remaining_capacity = serializers.IntegerField()
    capacity = serializers.IntegerField()
    class_time = serializers.CharField(max_length=50)
    exam_time = serializers.CharField(max_length=50)

    # اعتبارسنجی‌های اضافی
    # def validate_instructor_id(self, value):
    #     if not Instructor.objects.filter(id=value).exists():
    #         raise serializers.ValidationError("استاد پیدا نشد.")
    #     return value
    #
    # def validate_department_id(self, value):
    #     if not Department.objects.filter(id=value).exists():
    #         raise serializers.ValidationError("دانشکده پیدا نشد.")
    #     return value
class AddCourseResponseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer()
    department = DepartmentSerializer()

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'credits', 'instructor', 'department', 'capacity', 'remaining_capacity', 'class_time', 'exam_time']
