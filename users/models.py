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
        if not value:
            return
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
    message = "너무 큽니다...2MB 이하로 사진 용량을 줄여주세요."

    def __init__(self, limit_value=2 * 1024 * 1024, **kwargs):  # 2MB의 기본값 추가
        super().__init__(limit_value, **kwargs)  # 부모 클래스의 __init__ 호출

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
    username = models.CharField(max_length=20, unique=True)
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username.split()[0] if self.username else self.email.split("@")[0]

    def save(self, *args, **kwargs):
        if self.profile_picture:
            # 수동으로 실행하도록 변경 (마이그레이션 직렬화 문제)
            validator = MimeTypeValidator(["image/jpeg", "image/png"])
            validator(self.profile_picture)
        super().save(*args, **kwargs)
