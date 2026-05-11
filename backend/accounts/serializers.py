from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserSettings

User = get_user_model()

COMMON_FIELD_ERROR_MESSAGES = {
    "blank": "blank",
    "invalid": "invalid",
    "max_length": "max_length",
    "min_length": "min_length",
    "required": "required",
}


class UserSettingsSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(
        choices=UserSettings.LanguageChoices.choices,
        error_messages={**COMMON_FIELD_ERROR_MESSAGES, "invalid_choice": "invalid_choice"},
    )
    theme = serializers.ChoiceField(
        choices=UserSettings.ThemeChoices.choices,
        error_messages={**COMMON_FIELD_ERROR_MESSAGES, "invalid_choice": "invalid_choice"},
    )
    font_size = serializers.ChoiceField(
        choices=UserSettings.FontSizeChoices.choices,
        error_messages={**COMMON_FIELD_ERROR_MESSAGES, "invalid_choice": "invalid_choice"},
    )

    class Meta:
        model = UserSettings
        fields = ("language", "theme", "font_size")

class UserSerializer(serializers.ModelSerializer):
    settings = UserSettingsSerializer(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_active", "settings")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, error_messages=COMMON_FIELD_ERROR_MESSAGES)
    password_confirm = serializers.CharField(write_only=True, min_length=8, error_messages=COMMON_FIELD_ERROR_MESSAGES)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm")
        extra_kwargs = {
            "username": {
                "validators": [],
                "error_messages": COMMON_FIELD_ERROR_MESSAGES,
            },
            "email": {
                "validators": [],
                "error_messages": {**COMMON_FIELD_ERROR_MESSAGES, "invalid": "invalid_email"},
            },
        }

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("username_taken", code="username_taken")
        return value

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("email_taken", code="email_taken")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "passwords_do_not_match"},
                code="passwords_do_not_match",
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(error_messages=COMMON_FIELD_ERROR_MESSAGES)
    password = serializers.CharField(write_only=True, error_messages=COMMON_FIELD_ERROR_MESSAGES)

class ProfileUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        write_only=True,
        required=False,
        error_messages=COMMON_FIELD_ERROR_MESSAGES,
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        error_messages=COMMON_FIELD_ERROR_MESSAGES,
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        error_messages=COMMON_FIELD_ERROR_MESSAGES,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "current_password",
            "new_password",
            "new_password_confirm",
        )
        extra_kwargs = {
            "username": {
                "validators": [],
                "error_messages": COMMON_FIELD_ERROR_MESSAGES,
            },
            "email": {
                "validators": [],
                "error_messages": {**COMMON_FIELD_ERROR_MESSAGES, "invalid": "invalid_email"},
            },
        }

    def validate_username(self, value: str) -> str:
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username__iexact=value).exists():
            raise serializers.ValidationError("username_taken", code="username_taken")
        return value

    def validate_email(self, value: str) -> str:
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email__iexact=value).exists():
            raise serializers.ValidationError("email_taken", code="email_taken")
        return value

    def validate(self, attrs):
        wants_password_change = any(
            attrs.get(field) for field in ("current_password", "new_password", "new_password_confirm")
        )
        if wants_password_change:
            if not attrs.get("current_password"):
                raise serializers.ValidationError({"current_password": "current_password_required"})
            if not self.instance.check_password(attrs["current_password"]):
                raise serializers.ValidationError({"current_password": "current_password_incorrect"})
            if not attrs.get("new_password"):
                raise serializers.ValidationError({"new_password": "new_password_required"})
            if attrs.get("new_password") != attrs.get("new_password_confirm"):
                raise serializers.ValidationError(
                    {"new_password_confirm": "new_password_confirmation_mismatch"}
                )
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("current_password", None)
        new_password = validated_data.pop("new_password", None)
        validated_data.pop("new_password_confirm", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if new_password:
            instance.set_password(new_password)
        instance.save()
        return instance

class ConfirmPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, error_messages=COMMON_FIELD_ERROR_MESSAGES)

    def validate_current_password(self, value: str) -> str:
        request = self.context["request"]
        if not request.user.check_password(value):
            raise serializers.ValidationError("current_password_incorrect", code="current_password_incorrect")
        return value
