# forms.py
from django import forms

# forms.py
from django import forms

class registerForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=128, widget=forms.PasswordInput)
    user_level_id = forms.IntegerField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    national_id = forms.CharField(max_length=10)
    phone_number = forms.CharField(max_length=15)
    major = forms.CharField(max_length=100)
    year = forms.IntegerField()
    max_units = forms.IntegerField()
    student_number = forms.CharField(max_length=20)
    admission_year = forms.IntegerField()
    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if len(id_number) != 10:
            raise forms.ValidationError('شماره ملی باید ۱۰ رقم باشد.')
        return id_number

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
# forms.py
from django import forms

class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
# forms.py
class PasswordResetConfirmForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your username'}))
    reset_code = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'placeholder': 'Enter reset code'}))
    new_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}))
