from datetime import datetime, timedelta
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from auth_app.models import User, VerificationToken
from utils.common_methods import generate_serializer_error
from .serializers import RegistrationSerializer, LoginSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.db.utils import IntegrityError
import pytz
from utils.email import forget_password_email, send_account_activation_email

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
        user_id = serializer.data['id']
        user = User.objects.get(id=user_id)
        send_account_activation_email(user)
        return Response("Account created successfully.An account activation email is sent to your email id, please verify your account.", status=status.HTTP_201_CREATED)
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
        if user.is_active == True:
            return Response("Your email is already verified and account is activated.", status=status.HTTP_400_BAD_REQUEST)
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
@permission_classes([AllowAny])
def forget_password(request):
    try:
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user == None:
            return Response("User with given email doesn't exist.", status=status.HTTP_400_BAD_REQUEST)
        forget_password_email(user)
        return Response("A link has been sent to your registered email id to reset your password.Please check your email.", status=status.HTTP_200_OK)
    except (AssertionError, Exception) as err:
        return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def verify_reset_password_token(request, token):
    try:
        response = {}
        verification_token_obj = VerificationToken.objects.filter(
            token=token).first()
        if(verification_token_obj == None):
            response['type'] = "fail"
            response['message'] = "Token is invalid or expired.Please complete the procedure again to resend email."
        else:
            utc = pytz.UTC
            token_expiry_time = (
                verification_token_obj.created_at + timedelta(hours=24)).replace(tzinfo=utc)
            current_time = datetime.now().replace(tzinfo=utc)
            if(token_expiry_time < current_time):
                response['type'] = "fail"
                response['message'] = "Token is expired.Please complete the procedure again to resend email."
            else:
                response['type'] = "success"
                response['message'] = "Token verified successfully."
        return Response(response, status=status.HTTP_200_OK)
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
                response = "Token is expired.Please complete the procedure again to resend email."
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
