from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Users(AbstractBaseUser):
    username = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    previous_password = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.CharField(max_length=512, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UsersManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username.split()[0] if self.username else self.email.split("@")[0]
