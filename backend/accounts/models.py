from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=300, unique=True)

    def __str__(self) -> str:
        return self.username


class UserSettings(models.Model):
    class LanguageChoices(models.TextChoices):
        POLISH = "pl", "Polski"
        ENGLISH = "en", "English"

    class ThemeChoices(models.TextChoices):
        LIGHT = "light", "Light"
        DARK = "dark", "Dark"

    class FontSizeChoices(models.TextChoices):
        SMALL = "small", "75%"
        MEDIUM = "medium", "100%"
        LARGE = "large", "150%"
        XLARGE = "xlarge", "200%"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    language = models.CharField(max_length=10, choices=LanguageChoices.choices, default=LanguageChoices.POLISH)
    theme = models.CharField(max_length=20, choices=ThemeChoices.choices, default=ThemeChoices.LIGHT)
    font_size = models.CharField(max_length=20, choices=FontSizeChoices.choices, default=FontSizeChoices.MEDIUM)

    def __str__(self) -> str:
        return f"Settings for {self.user.username}"
