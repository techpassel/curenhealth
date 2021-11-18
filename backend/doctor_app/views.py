from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hospital_app.serializers import HospitalSerializer
from doctor_app.serializers import ConsultationSerializer, DoctorSerializer, QualificationSerializer, SpecialitySerializer
from hospital_app.models import Address, Hospital
from doctor_app.models import Doctor, Qualification, Speciality
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
    def get(self, request):
        try:
            doctors = Doctor.objects.all()
            serializer = DoctorSerializer(doctors, many=True) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    
    def put(self, request):
        try:
            data = request.data
            id = data.get("id")
            doctor = Doctor.objects.filter(id=id).first()
            if(doctor == None):
                return Response("Doctor not found", status=status.HTTP_400_BAD_REQUEST)
            for qual in data["qualification_set"]:
                q_serializer = None
                if "id" in qual:
                    qual_id = qual.get("id")
                    qualification = Qualification.objects.get(id=qual_id)
                    q_serializer = QualificationSerializer(qualification, data=qual, partial=True)
                else:
                    qual["doctor"] = doctor.id
                    q_serializer = QualificationSerializer(data=qual, partial=True)
                if not q_serializer.is_valid():
                    raise Exception(generate_serializer_error(q_serializer.errors))
                q_serializer.save()
            serializer = DoctorSerializer(doctor, data=data, partial=True)
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

