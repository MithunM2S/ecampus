from django.contrib.auth.models import AbstractUser
from django.db import models


class AuthUser(AbstractUser):
    email = models.EmailField('Email address', null=True)
    modules = models.CharField(
        'Accessable Modules',
        max_length=250,
        default=0)
