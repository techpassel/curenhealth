import secrets
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMessage
from auth_app.models import TokenType, VerificationToken
from auth_app.serializers import VerificationTokenSerializer
from .common_methods import generate_serializer_error


def send_account_activation_email(user):
    token = secrets.token_urlsafe(57)
    url = f'{settings.FRONTEND_BASE_URL}auth/activate-account/{token}'
    header_message = f"Hi {user.get_full_name()}.Thanks for registering with us. Please click on the button below to activate your account."
    html_template = 'email_verification_template.html'
    html_message = render_to_string(
        html_template, {'header_message': header_message, 'url': url})
    subject = 'Verify your email.'
    recipient_list = [user.email]
    token_type = TokenType.SIGNUP_EMAIL_VERIFICATION_TOKEN
    send_email(subject, html_message, recipient_list, user, token, token_type)


def forget_password_email(user):
    token = secrets.token_urlsafe(57)
    url = f'{settings.FRONTEND_BASE_URL}auth/verify-reset-password-token/{token}'
    header_message = f"Hi {user.get_full_name()}.Please click on the button below to reset your password."
    html_template = 'email_verification_template.html'
    html_message = render_to_string(
        html_template, {'header_message': header_message, 'url': url})
    subject = 'Reset your password.'
    recipient_list = [user.email]
    token_type = TokenType.RESET_PASSWORD_TOKEN
    send_email(subject, html_message, recipient_list, user, token, token_type)


def client_staff_activation_email(user, password, adding_user, unit_type, unit_name):
    token = secrets.token_urlsafe(57)
    url = f'{settings.FRONTEND_BASE_URL}auth/activate-account/{token}'
    user_first_name = None
    try:
        user_first_name = user['first_name']
    except:
        user_first_name = user.first_name
    user_email = None
    try:
        user_email = user['email']
    except:
        user_email = user.email
    header_message = f"Hi {user_first_name}. {adding_user} has added you as staff of {unit_type} - {unit_name}.You can activate your account by clicking on the button below. Upon activation of your account, you can login to your CureNHealth account by using ({user_email}) as email and ({password}) as password. But don't forget to reset your password after your first login."
    html_template = 'email_verification_template.html'
    html_message = render_to_string(
        html_template, {'header_message': header_message, 'url': url})
    subject = 'Verify your email.'
    recipient_list = [user_email]
    token_type = TokenType.CLIENT_STAFF_VERIFICATION_TOKEN
    send_email(subject, html_message, recipient_list, user, token, token_type)


def update_user_email(user, new_email, token_type=TokenType.UPDATE_EMAIL_VERIFICATION_TOKEN):
    token = secrets.token_urlsafe(57)
    url = f'{settings.FRONTEND_BASE_URL}user/update-email-verify/{token}'
    header_message = f"Hi {user.get_full_name()}.Please click on the button below to verify your email."
    html_template = 'email_verification_template.html'
    html_message = render_to_string(
        html_template, {'header_message': header_message, 'url': url})
    subject = 'Verify your email.'
    recipient_list = [new_email]
    token_type = token_type
    updating_value = new_email
    send_email(subject, html_message, recipient_list, user, token, token_type, updating_value)


def send_email(subject, html_message, recipient_list, user, token, token_type, token_updating_value=None):
    email_from = settings.DEFAULT_FROM_EMAIL
    message = EmailMessage(subject, html_message,
                           email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    user_id = None
    try:
        user_id = user["id"]
    except:
        user_id = user.id
    token_data = {
        'user': user_id,
        'token_type': token_type,
        'token': token
    }
    if token_updating_value != None:
        token_data["updating_value"] = token_updating_value
    existing_verification_token = VerificationToken.objects.filter(
        user=user_id,
        token_type=token_type).first()
    if existing_verification_token != None:
        existing_verification_token.delete()
    serializer = VerificationTokenSerializer(
        data=token_data, partial=True)
    if not serializer.is_valid():
        raise Exception(generate_serializer_error(serializer.errors))
    serializer.save()
