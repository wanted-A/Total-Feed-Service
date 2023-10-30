# from django.urls import path
# from .views import UserCreateView, LoginView, LogoutView

# urlpatterns = [
#     path("register/", UserCreateView.as_view(), name="register"),
#     path("login/", LoginView.as_view(), name="login"),
#     path("logout/", LogoutView.as_view(), name="logout"),
# ]

from django.urls import path
from .views import UserView, CustomLoginView, LogoutView

urlpatterns = [
    path("register/", UserView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
