# serializers.py

from rest_framework import serializers
from .models import User, Student  # فرض کنید مدل‌های User و Student شما اینجا تعریف شده‌اند


# serializers.py
# serializers.py
from rest_framework import serializers
from .models import User, Student, UserLevel

# serializers.py
from rest_framework import serializers
from .models import User, Student, UserLevel

class UserSerializer(serializers.ModelSerializer):
    user_level = serializers.PrimaryKeyRelatedField(queryset=UserLevel.objects.all())  # استفاده از شناسه برای فیلد user_level

    class Meta:
        model = User
        fields = ['username', 'password', 'user_level']  # اضافه کردن 'user_level'

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'national_id', 'phone_number',
                  'major', 'year', 'max_units', 'student_number', 'admission_year', 'user']
