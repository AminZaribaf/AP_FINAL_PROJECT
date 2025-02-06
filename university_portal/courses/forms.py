# forms.py

from django import forms

class AddCourseForm(forms.Form):
    course_name = forms.CharField(label='نام درس', max_length=100)
    course_code = forms.CharField(label='کد درس', max_length=10)
    credits = forms.IntegerField(label='تعداد واحد')
    instructor_id = forms.IntegerField(label='شناسه استاد')
    department_id = forms.IntegerField(label='شناسه دانشکده')
    capacity = forms.IntegerField(label='ظرفیت')
    exam_time= forms.CharField(label='زمان امتحان', max_length=100)
    class_time=forms.CharField(label='زمان درس', max_length=100)
    remaining_capacity=capacity = forms.IntegerField(label='ظرفیت باقی مانده')

# forms.py
from django import forms

class DeleteCourseForm(forms.Form):
    course_code = forms.CharField(label='کد درس', max_length=10)
