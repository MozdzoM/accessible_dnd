from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserSettings


# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("username", "email", "is_active", "is_staff")
    add_fieldsets = DjangoUserAdmin.add_fieldsets + ((None, {"fields": ("email",)}),)


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "language", "theme", "font_size")
    search_fields = ("user__username", "user__email")