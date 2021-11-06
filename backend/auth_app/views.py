from datetime import datetime, timedelta
import secrets
from django.conf import settings
from django.core.mail.message import EmailMessage
from django.http.response import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from auth_app.models import TokenType, User, VerificationToken
from utils.common_methods import generate_serializer_error
from .serializers import RegistrationSerializer, LoginSerializer, VerificationTokenSerializer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .renderers import UserJSONRenderer
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate
import pytz

@csrf_exempt
@api_view(['POST'])
# @renderer_classes([UserJSONRenderer])
@permission_classes([AllowAny])
# #Apply this where authentication is required.Import IsAuthenticated before use
def signup(request):
    try:
        user = request.data
        if 'id' in user:
            del user['id']
        serializer = RegistrationSerializer(data=user)
        if not serializer.is_valid():
            raise Exception(generate_serializer_error(serializer.errors))
        serializer.save()
        send_account_activation_email(serializer.data)
        return Response("Account created successfully.An account activation email is sent to your email is, please verify your account.", status=status.HTTP_201_CREATED)
    except IntegrityError as err:
        # IntegrityError in serializer.save() and not in serializer.is_valid() like incase of duplicate email etc.
        err = err.args[0].split("DETAIL:  Key")
        err = ((err[1].strip() if len(err) > 1 else err[0]).strip())
        return Response(err, status=status.HTTP_400_BAD_REQUEST)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
# @renderer_classes([UserJSONRenderer])
@permission_classes([AllowAny])
def resend_activation_email(request):
    try:
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user == None:
            return Response("Email not found.Please check your email.", status=status.HTTP_400_BAD_REQUEST)
        send_account_activation_email(user)
        return Response(status=status.HTTP_200_OK)
    except IntegrityError as err:
        err = err.args[0].split("DETAIL:  Key")
        err = ((err[1] if len(err) > 1 else err[0]).strip())
        return Response(err, status=status.HTTP_400_BAD_REQUEST)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_account_activation_email(user):
    token = secrets.token_urlsafe(57)
    url = f'{settings.FRONTEND_BASE_URL}auth/activate-account/{token}'
    header_message = f"Hi {user['first_name']}.Thanks for registering with us. Please click on the button below to activate your account."
    html_template = 'email_verification_template.html'
    html_message = render_to_string(
        html_template, {'header_message': header_message, 'url': url})
    subject = 'Verify your email.'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user['email'], ]
    message = EmailMessage(subject, html_message,
                           email_from, recipient_list)
    message.content_subtype = 'html'
    message.send()
    token_data = {
        'user': user['id'],
        'token_type': TokenType.SIGNUP_EMAIL_VERIFICATION_TOKEN,
        'token': token
    }
    existing_verification_token = VerificationToken.objects.filter(
        user=user['id'],
        token_type = TokenType.SIGNUP_EMAIL_VERIFICATION_TOKEN).first()
    if existing_verification_token != None:
        existing_verification_token.delete()
    serializer = VerificationTokenSerializer(
        data=token_data, partial=True)
    if not serializer.is_valid():
        raise Exception(generate_serializer_error(serializer.errors))
    serializer.save()
    return


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request, token):
    try:
        response = ""
        verification_token_obj = VerificationToken.objects.filter(
            token=token).first()
        if(verification_token_obj == None):
            response = "Token is invalid or expired.Please try to update your email again."
        else:
            utc = pytz.UTC
            token_expiry_time = (
                verification_token_obj.created_at + timedelta(hours=72)).replace(tzinfo=utc)
            current_time = datetime.now().replace(tzinfo=utc)
            if(token_expiry_time < current_time):
                response = "Token is expired.Please complete the procedure again to resend verification email."
            else:
                token_user = verification_token_obj.user
                new_data = {'is_active': True, 'is_email_verified': True}
                serializer = RegistrationSerializer(
                    instance=token_user, data=new_data, partial=True)
                if not serializer.is_valid():
                    raise Exception(generate_serializer_error(serializer.errors))
                serializer.save()
                response = "Account activated successfully."
                verification_token_obj.delete()
        return HttpResponse(response)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def forget_password(request):
    try:
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user == None:
            return Response("User with given email doesn't exist.", status=status.HTTP_400_BAD_REQUEST)
        token = secrets.token_urlsafe(57)
        url = f'{settings.FRONTEND_BASE_URL}auth/reset-password/{token}'
        header_message = f"Hi {user['first_name']}.Please click on the button below to reset your password."
        html_template = 'email_verification_template.html'
        html_message = render_to_string(
            html_template, {'header_message': header_message, 'url': url})
        subject = 'Reset your password.'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user['email'], ]
        message = EmailMessage(subject, html_message,
                            email_from, recipient_list)
        message.content_subtype = 'html'
        message.send()
        token_data = {
            'user': user['id'],
            'token_type': TokenType.RESET_PASSWORD_TOKEN,
            'token': token
        }
        existing_verification_token = VerificationToken.objects.filter(
            user=user['id'], 
            token_type = TokenType.RESET_PASSWORD_TOKEN).first()
        if existing_verification_token != None:
            existing_verification_token.delete()
        serializer = VerificationTokenSerializer(
            data=token_data, partial=True)
        if not serializer.is_valid():
            raise Exception(generate_serializer_error(serializer.errors))
        serializer.save()
        return
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    try:
        token = request.data.get('token')
        new_password= request.data.get('password')
        response = ""
        verification_token_obj = VerificationToken.objects.filter(
            token=token).first()
        if(verification_token_obj == None):
            response = "Token is invalid or expired.Please complete the procedure again to resend email."
        else:
            utc = pytz.UTC
            token_expiry_time = (
                verification_token_obj.created_at + timedelta(hours=24)).replace(tzinfo=utc)
            current_time = datetime.now().replace(tzinfo=utc)
            if(token_expiry_time < current_time):
                response = "Token is expired.Please try to update your email again."
            else:
                token_user = verification_token_obj.user
                new_data = {'password': new_password}
                serializer = RegistrationSerializer(
                    instance=token_user, data=new_data, partial=True)
                if not serializer.is_valid():
                    raise Exception(generate_serializer_error(serializer.errors))
                serializer.save()
                response = "Password reset successfully."
                verification_token_obj.delete()
        return HttpResponse(response)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
# @renderer_classes([UserJSONRenderer])
def login(request):
    try:
        user = request.data
        # Notice here that we do not call `serializer.save()` like we did in signup.
        # This is because we don't have anything to save. Instead, the `validate` method on our
        # serializer handles everything we need.
        serializer = LoginSerializer(data=user)
        if not serializer.is_valid():
            errors = ""
            for key in serializer.errors:
                errors += (key+" - "+serializer.errors[key][0]) + (
                    ", " if (list(serializer.errors)[-1] != key) else "")
            raise Exception(errors)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
