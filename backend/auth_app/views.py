from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .renderers import UserJSONRenderer
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate

@csrf_exempt
@api_view(['POST'])
# @renderer_classes([UserJSONRenderer])
@permission_classes([AllowAny])
# #Apply this where authentication is required.Import IsAuthenticated before use
def signup(request):
    try:
        user = request.data;
        if 'id' in user:
            del user['id'];
        # The create serializer, validate serializer, save serializer pattern is common in all view in django rest framework
        serializer = RegistrationSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except IntegrityError as err:      
        err = err.args[0].split("DETAIL:  Key")
        err = ((err[1] if len(err) > 1 else err[0]).strip())
        return Response(err, status=status.HTTP_406_NOT_ACCEPTABLE)
    except :
        return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    response = {}
    try:
        # Important for format
        usertype = request.user.usertype
        # Here we are not using it but we can use it for URLs which have permission for any specific type of use only.
        email = request.data.get('email')
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        user = authenticate(username=email, password=old_password)

        if user is None:
            raise Exception(
                'User with given email and password not found.'
            )
        formatted_data = {"email": email, "password": new_password}
        serializer = RegistrationSerializer(user, data=formatted_data, partial=True)
        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response['msg'] = "Password changed"
        return Response(response, status=status.HTTP_202_ACCEPTED)
    except Exception as err:
        # print(type(err))
        response['error'] = err.args[0]
        return Response(response, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
# @renderer_classes([UserJSONRenderer])
def login(request):

    user = request.data
    # Notice here that we do not call `serializer.save()` like we did for
    # the registration endpoint. This is because we don't  have
    # anything to save. Instead, the `validate` method on our serializer
    # handles everything we need.
    serializer = LoginSerializer(data=user)
    serializer.is_valid(raise_exception=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

