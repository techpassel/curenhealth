from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view

@api_view(['POST'])
@csrf_exempt
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    """
    Request body format
    {
        "first_name": "Aman",
        "last_name": "Saurabh",
        "email": "aaman423@gmail.com",
        "password": "123456",
        "country_code": "+91",
        "contact_num": 7320865821,
        "usertype": "USER"
    }
    """