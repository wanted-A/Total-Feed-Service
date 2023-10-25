from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.urls import reverse
import os

from .models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com"
        )
        self.user.set_password("testpass")
        self.user.save()
        self.client.force_login(self.user)
        self.mock_file = SimpleUploadedFile(
            "testfile.txt", b"file_content", content_type="text/plain"
        )

    def test_file_upload(self):
        mock_image_content = b"\xFF\xD8\xFF\xE0" + b"0" * 508 + b"\xFF\xD9"
        self.mock_file = SimpleUploadedFile(
            "testfile.jpg", mock_image_content, content_type="image/jpeg"
        )

        response = self.client.post(
            reverse("user-list"),
            {
                "username": "newtestuser",
                "email": "newtestuser@example.com",
                "profile_picture": self.mock_file,
            },
        )
        self.assertEqual(response.status_code, 200)
        instance = User.objects.get(profile_picture="testfile.jpg")
        self.assertTrue(instance.profile_picture)

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("testpass"))

    def test_user_should_validate_image_size(self):
        large_file_content = os.urandom(3 * 1024 * 1024)
        large_file = SimpleUploadedFile(
            "large_image.jpg", large_file_content, content_type="image/jpeg"
        )
        self.user.profile_picture = large_file
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_user_should_return_username(self):
        self.assertEqual(self.user.get_full_name(), "testuser")
        self.assertEqual(self.user.get_short_name(), "testuser")

    def tearDown(self):
        self.user.profile_picture.delete(save=False)
