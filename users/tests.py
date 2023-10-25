from django.test import TestCase
from .models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com"
        )
        self.user.set_password("testpass")
        self.user.save()
        self.client.force_login(self.user)

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("testpass"))

    def test_user_should_return_username(self):
        self.assertEqual(self.user.get_full_name(), "testuser")
        self.assertEqual(self.user.get_short_name(), "testuser")

    def tearDown(self):
        self.user.profile_picture.delete(save=False)
