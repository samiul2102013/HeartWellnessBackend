import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import User
from .serializers import (
    RegisterSerializer, UserProfileSerializer,
    ChangePasswordSerializer, AdminUserSerializer,
    VerifyEmailSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
)
from .utils import send_verification_email, send_password_reset_email
from apps.core.permissions import IsAdminRole

PASSWORD_RESET_EXPIRY_HOURS = 1


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        if not user.email_verify_token:
            user.email_verify_token = str(uuid.uuid4())
            user.save(update_fields=['email_verify_token'])
        # Send verification email right after registration
        send_verification_email(user, self.request)


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Password updated successfully.'})


# ── Email Verification ────────────────────────────────────────

class VerifyEmailView(APIView):
    """
    User clicks link from email → hits this endpoint with token.
    Works for both mobile deep links and web.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = str(serializer.validated_data['token'])
        try:
            user = User.objects.get(email_verify_token=token)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid verification token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.email_verified:
            return Response({'detail': 'Email already verified.'})

        user.email_verified = True
        user.email_verify_token = None
        user.save(update_fields=['email_verified', 'email_verify_token'])
        return Response({'detail': 'Email verified successfully.'})


class ResendVerificationEmailView(APIView):
    """Authenticated user can resend their verification email."""

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response(
                {'detail': 'Email is already verified.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        send_verification_email(user, request)
        return Response({'detail': 'Verification email sent.'})


# ── Forgot / Reset Password ───────────────────────────────────

class ForgotPasswordView(APIView):
    """
    Takes email → generates reset token → sends email.
    Always returns 200 to prevent user enumeration.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        # Always return 200 even if email not found
        if not serializer.is_valid():
            return Response({'detail': 'If this email exists, a reset link will be sent.'})

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            user.password_reset_token = str(uuid.uuid4())
            user.password_reset_token_created = timezone.now()
            user.save(update_fields=['password_reset_token', 'password_reset_token_created'])
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass  # Silent — don't leak user existence

        return Response({'detail': 'If this email exists, a reset link will be sent.'})


class ResetPasswordView(APIView):
    """
    Takes token + new_password → validates token expiry → resets password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = str(serializer.validated_data['token'])
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(password_reset_token=token)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check token expiry
        expiry = user.password_reset_token_created + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)
        if timezone.now() > expiry:
            return Response(
                {'detail': 'Reset token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_token_created = None
        user.save(update_fields=['password', 'password_reset_token', 'password_reset_token_created'])

        return Response({'detail': 'Password reset successfully. You can now log in.'})


# ── Admin Views ───────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['plan', 'is_active', 'role', 'email_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name']


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]