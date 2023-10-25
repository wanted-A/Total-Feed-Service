from django.test import TestCase
from .models import User, PreviousPassword


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.client.force_login(self.user)

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("testpass"))

    def test_user_should_return_username(self):
        self.assertEqual(self.user.get_full_name(), "testuser")
        self.assertEqual(self.user.get_short_name(), "testuser")


def test_previous_passwords(self):
    # 1차 비밀번호 변경
    self.user.set_password("newpass1")
    self.assertEqual(PreviousPassword.objects.filter(user=self.user).count(), 1)

    # 2차 비밀번호 변경
    self.user.set_password("newpass2")
    self.assertEqual(PreviousPassword.objects.filter(user=self.user).count(), 2)

    # 3차 비밀번호 변경 (첫 번째 비밀번호로 변경)
    self.user.set_password("newpass1")
    self.assertEqual(PreviousPassword.objects.filter(user=self.user).count(), 2)
    self.assertFalse(
        any(
            check_password("testpass", pass_entry.password)
            for pass_entry in PreviousPassword.objects.filter(user=self.user)
        )
    )
    self.assertFalse(
        any(
            check_password("newpass1", pass_entry.password)
            for pass_entry in PreviousPassword.objects.filter(user=self.user)
        )
    )
    self.assertTrue(
        any(
            check_password("newpass2", pass_entry.password)
            for pass_entry in PreviousPassword.objects.filter(user=self.user)
        )
    )
    self.assertTrue(self.user.check_password("newpass1"))

    # 4차 비밀번호 변경 - 다시 중복으로 시도
    self.user.set_password("newpass1")
    self.assertTrue(self.user.check_password("newpass1"))

    def tearDown(self):
        self.user.profile_picture.delete(save=False)
