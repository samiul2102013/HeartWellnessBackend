from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'password', 'password2']

    def validate_email(self, value):
        return value.lower().strip()
            
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'avatar', 'plan', 'role', 'created_at']
        read_only_fields = ['id', 'plan', 'role', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
 
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

# ── Email verification ────────────────────────────────────────
 
class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.UUIDField()
 
 
# ── Forgot / Reset password ───────────────────────────────────
 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
 
    def validate_email(self, value):
        value = value.lower().strip()
        if not User.objects.filter(email=value).exists():
            # Return same message to avoid user enumeration
            raise serializers.ValidationError(
                'If this email exists, a reset link will be sent.'
            )
        return value
 
 
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
 
# Admin serializers
class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone_number', 'avatar', 'plan', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']