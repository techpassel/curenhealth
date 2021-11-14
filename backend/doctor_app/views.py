from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hospital_app.serializers import HospitalSerializer
from doctor_app.serializers import ConsultationSerializer, DoctorSerializer, QualificationSerializer, SpecialitySerializer
from hospital_app.models import Address, Hospital
from doctor_app.models import Speciality
from utils.common_methods import generate_serializer_error

# Create your views here.
class SpecialityView(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request):
        try:
            data = request.data
            if ("related_speciality_id" in data) and (data["related_speciality_id"] != (None or "")):
                related_speciality = Speciality.objects.get(id=data["related_speciality_id"])
                data["related_speciality"] = related_speciality.id
            del data["related_speciality_id"]    
            serializer = SpecialitySerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            data = request.data
            serializer = DoctorSerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultationView(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request):
        try:
            data = request.data
            if ("hospital_id" in data) and (data["hospital_id"] != (None or "")):
                hospital_id = data.get("hospital_id")
                hospital = Hospital.objects.get(id=hospital_id)
                data["hospital"] = hospital
                del data["hospital_id"]
            if ("address_id" in data) and (data["address_id"] != (None or "")):
                address_id = data.get("address_id")
                address = Address.objects.get(id=address_id)
                data["address"] = address
                del data["hospital_id"]
            serializer = ConsultationSerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

