from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    previous_password = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.CharField(max_length=512, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
