from django.db import models
from datetime import date
from django.core.validators import RegexValidator
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .manager import UserManager 
# Function to handle file upload paths
def user_directory_path1(instance, filename):
    return os.path.join('upload_images/profile_images', f'{instance.c_email}', filename)


def user_directory_path2(instance, filename):
    return os.path.join('upload_images/resume', f'{instance.c_email}', filename)


# Candidate Model for user profile
class Candidate(models.Model):
    c_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    c_first_name = models.CharField(max_length=20, blank=False)
    c_last_name = models.CharField(max_length=20, blank=False)
    c_father_name = models.CharField(max_length=50, blank=False)
    c_mother_name = models.CharField(max_length=50, blank=False)
    c_email = models.EmailField(unique=True)
    c_contact_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")
        ],
    )
    c_dob = models.DateField()  # Date of Birth

    # Choices for Gender
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    c_sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Address Information
    c_city = models.CharField(max_length=50, blank=False)
    c_state = models.CharField(max_length=50, blank=False)
    country = models.CharField(max_length=50, blank=False)

    # File Uploads
    c_pic = models.ImageField(upload_to=user_directory_path1, blank=True, null=True)
    c_resume = models.FileField(upload_to=user_directory_path2, blank=True, null=True)
    c_skills = models.CharField(max_length=100, blank=True, null=True)

    # Other Details
    c_registration_date = models.DateField(default=date.today)  # Auto-set the registration date
    time_slot = models.DateTimeField()  # Scheduled test time slot

    # Dynamically calculated age
    @property
    def age(self):
        today = date.today()
        return today.year - self.c_dob.year - ((today.month, today.day) < (self.c_dob.month, self.c_dob.day))

    def __str__(self):
        return f"{self.c_first_name} {self.c_last_name}"


# Custom User Model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True, blank=True)

    # Required fields for User model
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']   # You can add other required fields if necessary

    def __str__(self):
        return self.username




