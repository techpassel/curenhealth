from datetime import datetime, timedelta
from functools import partial
from json.encoder import JSONEncoder
from django.contrib.auth import authenticate
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import TokenType, User, VerificationToken
from auth_app.serializers import RegistrationSerializer, VerificationTokenSerializer
from hospital_app.models import Address
from .serializers import UserDetailsSerializer, UserSerializer
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import secrets
import json
import pytz
# Create your views here.


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return Response("Wait")

    def post(self, request, format=None):
        data = request.data
        user_id = data.get("user_id")
        address_id = data.get("address_id")
        user = User.objects.get(id=user_id)
        address = Address.objects.get(id=address_id)
        del data["user_id"]
        del data["address_id"]
        data["user"] = user.id
        data["address"] = address.id
        serializer = UserDetailsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user_instance = User.objects.get(id=user_id)
        user_instance.delete()
        return Response(status=status.HTTP_200_OK)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty", status=status.HTTP_406_NOT_ACCEPTABLE)
            restricted_items = ['email', 'password']
            for key in restricted_items:
                if key in user_data:
                    return Response(f"{key} can't be changed from this api.", status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(id=user_data['id'])
            serializer = UserSerializer(instance=user, data=user_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as err:
            err = err.args[0].split("DETAIL:  Key")
            err = ((err[1] if len(err) > 1 else err[0]).strip())
            return Response(err, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty", status=status.HTTP_406_NOT_ACCEPTABLE)
            user = User.objects.get(id=user_data['id'])
            current_password = user_data['current_password']
            auth_user = authenticate(
                username=user.email, password=current_password)
            if auth_user is None:
                return Response('User not found.', status=status.HTTP_406_NOT_ACCEPTABLE)
            new_data = {"password": user_data["new_password"]}
            serializer = RegistrationSerializer(
                instance=user, data=new_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        except IntegrityError as err:
            err = err.args[0].split("DETAIL:  Key")
            err = ((err[1] if len(err) > 1 else err[0]).strip())
            return Response(err, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEmailRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty.", status=status.HTTP_406_NOT_ACCEPTABLE)
            email_user = User.objects.filter(
                email=user_data['new_email']).first()
            if email_user != None:
                return Response("New email you provided already exists.", status=status.HTTP_406_NOT_ACCEPTABLE)
            user = User.objects.get(id=user_data['id'])
            if user.email != user_data['current_email']:
                return Response("Current email did not matched with your stored data.", status=status.HTTP_406_NOT_ACCEPTABLE)
            token = secrets.token_urlsafe(57)
            url = f'{settings.FRONTEND_BASE_URL}user/update-email-verify/{token}'
            html_template = 'update_email_verification.html'
            html_message = render_to_string(
                html_template, {'name': user.get_full_name(), 'url': url})
            subject = 'Verify your email.'
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user_data['new_email'], ]
            message = EmailMessage(subject, html_message,
                                   email_from, recipient_list)
            message.content_subtype = 'html'
            message.send()
            token_data = {
                'user': user.id,
                'token_type': TokenType.UPDATE_EMAIL_VERIFICATION_TOKEN,
                'token': token,
                'updating_value': user_data['new_email']}
            
            existing_verification_token = VerificationToken.objects.filter(
                user=user).first()
            if existing_verification_token != None:
                existing_verification_token.delete()
            serializer = VerificationTokenSerializer(
                data=token_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, verification_token):
        try:
            response = ""
            verification_token_obj = VerificationToken.objects.filter(token=verification_token).first();
            if(verification_token_obj == None):
                response = "Token is invalid or expired.Please try to update your email again."
            else:
                utc=pytz.UTC
                token_expiry_time = (verification_token_obj.created_at + timedelta(hours=24)).replace(tzinfo=utc)
                current_time = datetime.now().replace(tzinfo=utc)
                if(token_expiry_time < current_time):
                    response = "Token is expired.Please try to update your email again. - {token_expiry_time} - {current_time}"
                else:
                    new_email = verification_token_obj.updating_value
                    token_user = verification_token_obj.user;
                    new_data = {"email": new_email}
                    serializer = RegistrationSerializer(
                        instance=token_user, data=new_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    response = "Email updated successfully"
                    verification_token_obj.delete()
            return HttpResponse(response)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
