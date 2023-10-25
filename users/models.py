from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("유효한 이메일 주소를 입력하세요.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    previous_password = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        blank=True,
        null=True,
    )
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username.split()[0] if self.username else self.email.split("@")[0]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
