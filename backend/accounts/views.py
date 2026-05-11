# from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import UserSettings
from .serializers import (
    ConfirmPasswordSerializer,
    LoginSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
    UserSettingsSerializer,
)


def api_error(code: str, response_status: int, **params) -> Response:
    return Response(
        {"detail": {"code": code, **params}},
        status=response_status,
    )

def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    max_age = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE,
        refresh_token,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=max_age,
        path="/",
    )

def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(settings.JWT_REFRESH_COOKIE, path="/")


# Create your views here.
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return api_error("invalid_credentials", status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return api_error("account_inactive", status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"access": str(refresh.access_token), "user": UserSerializer(user).data},
            status=status.HTTP_200_OK,
        )
        set_refresh_cookie(response, str(refresh))
        return response
    
class RefreshView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not refresh_token:
            return api_error("missing_refresh_token", status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError, ValidationError):
            return api_error("invalid_refresh_token", status.HTTP_401_UNAUTHORIZED)
        response = Response({"access": serializer.validated_data["access"]}, status=status.HTTP_200_OK)
        if "refresh" in serializer.validated_data:
            set_refresh_cookie(response, serializer.validated_data["refresh"])
        return response
    
class LogoutView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request: Request) -> Response:
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response

class MeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)

    def delete(self, request: Request) -> Response:
        serializer = ConfirmPasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response
    
class SettingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request) -> Response:
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        return Response(UserSettingsSerializer(user_settings).data)

    def patch(self, request: Request) -> Response:
        user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(user_settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    