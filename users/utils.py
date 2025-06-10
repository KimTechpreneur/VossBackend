from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import secrets
import string

def generate_secure_password(length=12):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure password meets minimum requirements
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

def generate_reset_token():
    """Generate a secure token for password reset."""
    return secrets.token_urlsafe(32)

def send_password_reset_email(user, reset_url):
    """Send password reset email to user."""
    context = {
        'user': user,
        'reset_url': reset_url,
        'expiry_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,  # Convert seconds to hours
        'current_year': timezone.now().year
    }
    
    html_message = render_to_string('users/emails/password_reset.html', context)
    
    send_mail(
        subject='Password Reset Request - Voss',
        message=f'Please reset your password by visiting: {reset_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )

def send_user_invitation_email(user, setup_url, temporary_password):
    """Send account setup invitation email to new user."""
    context = {
        'user': user,
        'setup_url': setup_url,
        'temporary_password': temporary_password,
        'expiry_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,  # Convert seconds to hours
        'current_year': timezone.now().year
    }
    
    html_message = render_to_string('users/emails/user_invitation.html', context)
    
    send_mail(
        subject='Welcome to Voss - Set Up Your Account',
        message=f'Your account has been created. Please set up your account by visiting: {setup_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message
    )

def validate_password_strength(password):
    """
    Validate password strength according to requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    
    if not any(c in string.punctuation for c in password):
        return False, "Password must contain at least one special character."
    
    return True, None 