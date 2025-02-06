from random import randint
from django.http import JsonResponse
from django.views import View
from .models import User , Student
from django.shortcuts import render

from django.views import View
from django.http import JsonResponse
import json
from .forms import registerForm
# views.py
from django.http import JsonResponse
from django.shortcuts import render
from .models import User, Student
from .serializer import UserSerializer, StudentSerializer
from django.views import View
import json

# views.py
from django.http import JsonResponse
from django.shortcuts import render
from .models import User, Student, UserLevel
from .serializer import UserSerializer, StudentSerializer
from django.views import View
import json

# views.py
from django.http import JsonResponse
from .models import User, Student, UserLevel
from .serializer import UserSerializer, StudentSerializer
from django.views import View
import json

# views.py
from django.http import JsonResponse
from .models import User, Student, UserLevel
from .serializer import UserSerializer, StudentSerializer
from django.views import View
import json

class RegisterUserView(View):
    def get(self, request):
        form = registerForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        try:
            # Deserialize incoming JSON data
            data = json.loads(request.body)

            # دریافت شناسه user_level_id از داده‌های ورودی
            user_level_id = data.get('user_level_id')

            # دریافت شیء UserLevel از پایگاه داده
            try:
                user_level = UserLevel.objects.get(id=user_level_id)  # دریافت شیء UserLevel بر اساس شناسه
            except UserLevel.DoesNotExist:
                return JsonResponse({'error': 'Invalid user level ID'}, status=400)

            user_data = {
                'username': data.get('username'),
                'password': data.get('password'),
                'user_level': user_level.id,  # فقط شناسه user_level را ارسال می‌کنیم، نه شیء کامل
            }

            student_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'email': data.get('email'),
                'national_id': data.get('national_id'),
                'phone_number': data.get('phone_number'),
                'major': data.get('major'),
                'year': data.get('year'),
                'max_units': data.get('max_units'),
                'student_number': data.get('student_number'),
                'admission_year': data.get('admission_year'),
            }

            # Validate and create user
            user_serializer = UserSerializer(data=user_data)
            if not user_serializer.is_valid():
                return JsonResponse({'error': user_serializer.errors}, status=400)

            # Save the user
            user = user_serializer.save()

            # Validate and create student
            student_data['user'] = user.id
            student_serializer = StudentSerializer(data=student_data)
            if not student_serializer.is_valid():
                return JsonResponse({'error': student_serializer.errors}, status=400)

            # Save the student
            student = student_serializer.save()

            return JsonResponse(
                {'message': 'Student registered successfully', 'student_id': student.id},
                status=201
            )

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

from .forms import LoginForm
class LoginUserView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'نام کاربری نا معتبر'}, status=401)


        # حالا برای اعتبارسنجی پسورد هش‌شده از check_password کمک می‌گیریم
        if password==user.password:
            return JsonResponse({'message': 'Login successful', 'user_id': user.id}, status=200)
        else:
            return JsonResponse({'error': 'رمز عبور نامعتبر'}, status=401)


password_reset_codes = {}

class PasswordResetRequestView(View):
    def post(self, request):
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # تولید کد تصادفی ۶ رقمی
        reset_code = randint(100000, 999999)
        password_reset_codes[username] = reset_code

        return JsonResponse({'message': 'Reset code generated', 'reset_code': reset_code})


class PasswordResetConfirmView(View):
    def post(self, request):
        username = request.POST.get('username')
        reset_code = int(request.POST.get('reset_code'))
        new_password = request.POST.get('new_password')

        if username not in password_reset_codes or password_reset_codes[username] != reset_code:
            return JsonResponse({'error': 'Invalid reset code'}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

        # Store new password in plain text
        user.password = new_password
        user.save()

        # Remove reset code from temporary storage
        del password_reset_codes[username]

        return JsonResponse({'message': 'Password reset successfully'})

from random import randint


