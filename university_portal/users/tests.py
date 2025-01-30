from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
from .models import User, UserLevel
from .views import password_reset_codes


from django.test import TestCase, Client
from .models import User, UserLevel

class RegisterUserViewTest(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()

        # Create a user level (e.g., Student)
        self.user_level = UserLevel.objects.create(name="Student")

    def test_register_user_success(self):
        # Send request to register a new user
        response = self.client.post('/api/users/register/', {
            'username': 'testuser',
            'password': 'password123',  # Plain text password
            'user_level_id': self.user_level.id
        })

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('User registered successfully', response.json().get('message'))


class LoginUserViewTest(TestCase):
    def setUp(self):
        # Create a user level
        self.user_level = UserLevel.objects.create(name="Student")

        # Create a test user with a plain text password
        self.user = User.objects.create(
            username='testuser',
            password='password123',  # No hashing
            user_level=self.user_level
        )

        # Create a test client
        self.client = Client()

    def test_login_success(self):
        # Send request to login
        response = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'password123'  # Plain text password
        })

        # Check if login was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('Login successful', response.json().get('message'))


class PasswordResetTest(TestCase):
    def setUp(self):
        # Create a test user level
        self.user_level = UserLevel.objects.create(name="Student")

        # Create a test user
        self.user = User.objects.create(
            username='testuser',
            password='password123',  # Plain text password
            user_level=self.user_level
        )

        # Create a test client
        self.client = Client()

    def test_password_reset_request(self):
        # Send request for password reset
        response = self.client.post('/api/users/password-reset/', {'username': 'testuser'})

        # Check if the reset request was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('Reset code generated', response.json().get('message'))

    def test_password_reset_confirm(self):
        # Request a reset code
        self.client.post('/api/users/password-reset/', {'username': 'testuser'})

        # Get the reset code from the temporary storage
        reset_code = password_reset_codes['testuser']

        # Send request to reset the password
        response = self.client.post('/api/users/password-reset-confirm/', {
            'username': 'testuser',
            'reset_code': reset_code,
            'new_password': 'newpass123'  # Plain text password
        })

        # Check if the password reset was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn('Password reset successfully', response.json().get('message'))
