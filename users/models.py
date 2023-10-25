from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password


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
    username = models.CharField(max_length=20, unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    previous_password = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="assets/profile_pictures",
        blank=True,
        null=True,
    )
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    def get_short_name(self):
        return self.first_name or self.username.split()[0]

    def set_password(self, raw_password):
        """
        비밀번호를 해시하여 저장
        """

        # 이전 비밀번호(1개 이력만)를 저장
        self.previous_password = self.password

        # 새로운 비밀번호를 해시하여 저장
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_previous_password(self, raw_password):
        """
        이전 비밀번호와 현재 입력된 비밀번호를 비교하는 메서드
        """
        return check_password(raw_password, self.previous_password)
