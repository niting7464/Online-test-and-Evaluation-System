from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User Model
    """
    is_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

