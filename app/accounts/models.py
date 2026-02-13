from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_GENERAL = 0
    ROLE_ADMIN_L1 = 1
    ROLE_ADMIN_L2 = 2

    ROLE_CHOICES = (
        (ROLE_GENERAL, "general"),
        (ROLE_ADMIN_L1, "admin_l1"),
        (ROLE_ADMIN_L2, "admin_l2"),
    )

    role_level = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=ROLE_GENERAL)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=32)
    age = models.PositiveIntegerField()
    department = models.CharField(max_length=255)
    is_target = models.BooleanField(default=False)
