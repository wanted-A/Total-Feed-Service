from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError

# MIME 타입 검사를 위한 라이브러리 (이미지 사진 업로드)
import magic


class MimeTypeValidator:
    def __init__(self, mimetypes):
        self.mimetypes = mimetypes

    def __call__(self, value):
        try:
            mime = magic.Magic(mime=True)
            file_mime = mime.from_buffer(value.read())
            if file_mime not in self.mimetypes:
                raise ValidationError(
                    f"Invalid file type. Allowed types are: {', '.join(self.mimetypes)}"
                )
        except Exception as e:
            raise ValidationError(f"Error reading file: {e}")
        finally:
            value.seek(0)


# 이미지 검증기를 클래스로 변경
class ImageSizeValidator(BaseValidator):
    limit = 2 * 1024 * 1024  # 2MB
    message = "File too large. Size should not exceed 2 MiB."

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return x.file.size


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
    username = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    previous_password = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        validators=[
            ImageSizeValidator(),
            MimeTypeValidator(["image/jpeg", "image/png"]),
        ],
        blank=True,
        null=True,
    )
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username.split()[0] if self.username else self.email.split("@")[0]
