from django.db import models

class UserLevel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    user_level = models.ForeignKey(UserLevel, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    @classmethod
    def create_user(cls, username, password, user_level_id=None):
        # Custom method to create a user with hashed password
        from django.contrib.auth.hashers import make_password
        user = cls(
            username=username,
            password=make_password(password),
            user_level_id=user_level_id
        )
        user.save()
        return user


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    national_id = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    major = models.CharField(max_length=100)
    year = models.IntegerField()
    max_units = models.IntegerField()
    student_number = models.CharField(max_length=20, unique=True)
    admission_year = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_number})"
