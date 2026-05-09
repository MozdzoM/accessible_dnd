from django.urls import path

from .views import LoginView, LogoutView, MeView, RefreshView, RegisterView, SettingsView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", RefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    path("settings/", SettingsView.as_view(), name="settings"),
]