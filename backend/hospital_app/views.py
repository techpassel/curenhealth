from functools import partial
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User
from utils.common_methods import generate_serializer_error
from hospital_app.models import Address, City
from hospital_app.serializers import AddressSerializer, CitySerializer, HospitalSerializer

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
        serializer = AddressSerializer(data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAddressView(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request, id):
        try:
            address = Address.objects.select_related("city").filter(pk=id).first()
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)

class HospitalView(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request):
        try:
            data = request.data
            hospital_admin_id = data.get("hospital_admin_id")
            hospital_admin = User.objects.get(id=hospital_admin_id)
            data["hospital_admin"] = hospital_admin.id
            del data["hospital_admin_id"]
            if "address" in data and data["address"] != "":
                addr_serializer = AddressSerializer(data=data["address"])
                if not addr_serializer.is_valid():
                    raise Exception(generate_serializer_error(addr_serializer.errors))
                addr_serializer.save()
                data["address"] = addr_serializer.data.get('id')
            serializer = HospitalSerializer(data=data)            
            if not serializer.is_valid():
                print(serializer.errors,"serializer.errors")
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
