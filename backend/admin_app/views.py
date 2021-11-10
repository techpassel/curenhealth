from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from auth_app.models import UserType

from user_app.serializers import SubscriptionSchemesSerializer
from utils.common_methods import generate_serializer_error, verify_admin

# Create your views here.
class SubscriptionSchemesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Call this 'verify_admin' method in every "view" methods of admin app.
            verify_admin(request.user);
            data = request.data
            serializer = SubscriptionSchemesSerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)