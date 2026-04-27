from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user, request):
    token = str(user.email_verify_token)
    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"
    
    send_mail(
        subject="Verify your HeartBeat Harmony email",
        message = (
            f"Hi {user.username}, \n\n"
            f"Please verify your email by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"Thank you!"       
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently=False,
                
    )
    
def send_password_reset_email(user):
    token = str(user.password_reset_token)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={token}"
    send_mail(
        subject="Reset your HeartBeat Harmony password",
        message = (
            f"Hi {user.username}, \n\n"
            f"You requested a password reset. Click the link below to set a new password:\n\n"
            f"{reset_url}\n\n"
            f"If you didn't request this, please ignore this email."       
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [user.email],
        fail_silently=False,
    )