from random import randint
from django.http import JsonResponse
from django.views import View
from .models import User


class RegisterUserView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')  # Store password in plain text
        user_level_id = request.POST.get('user_level_id')

        if not username or not password or not user_level_id:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        # Create a new user without hashing the password
        user = User.objects.create(username=username, password=password, user_level_id=user_level_id)
        return JsonResponse({'message': 'User registered successfully', 'user_id': user.id})



class LoginUserView(View):
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        # Compare plain text password
        if password == user.password:
            return JsonResponse({'message': 'Login successful', 'user_id': user.id})

        return JsonResponse({'error': 'Invalid credentials'}, status=401)


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
