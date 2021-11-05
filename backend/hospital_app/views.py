from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User
from hospital_app.models import City
from hospital_app.serializers import AddressSerializer, CitySerializer

# Create your views here.
class CityView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data = request.data
        added_by_id = data.get("added_by_id");
        user = User.objects.get(id=added_by_id);
        del data["added_by_id"]
        print(user.first_name,"User")
        data["added_by"] = user.id
        serializer = CitySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AddressView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data = request.data
        city_id = data.get("city_id");
        city = City.objects.get(id=city_id);
        del data["city_id"]
        data["city"] = city.id
        serializer = AddressSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)