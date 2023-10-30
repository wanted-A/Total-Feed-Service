from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "User Profile",
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                    "is_approved",
                    "is_active",
                )
            },
        ),
    )
    list_display = ("id", "username", "email", "is_approved", "is_active")
    list_display_links = ("id", "username", "email")
