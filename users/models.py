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


MAX_PREVIOUS_PASSWORDS = 2  # 2개 까지는 중복 비밀번호 불허하나, 3개부터는 재사용을 허가합니다.


class PreviousPassword(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)


class User(AbstractBaseUser):
    username = models.CharField(max_length=20, unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
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

        # 기존 비밀번호가 있을 때만 이전 비밀번호로 저장
        if self.password and self.pk:  # self.pk를 확인하여 데이터베이스에 이미 저장되었는지 확인.
            PreviousPassword.objects.create(user=self, password=self.password)

            # 이전 비밀번호가 설정된 최대 개수를 초과 시, 가장 오래된 것부터 삭제
            while self.PreviousPassword_set.count() > MAX_PREVIOUS_PASSWORDS:
                self.PreviousPassword_set.earliest("created_at").delete()

        # 새로운 비밀번호를 해시하여 저장
        self.password = make_password(raw_password)
        if self.pk:  # 여기도 self.pk를 확인합니다.
            self.save(update_fields=["password"])

    def check_previous_passwords(self, raw_password):
        """
        입력된 비밀번호가 이전 비밀번호 중 하나와 일치하는지 확인
        """
        return any(
            check_password(raw_password, prev_pass.password)
            for prev_pass in self.PreviousPassword_set.all()
        )
