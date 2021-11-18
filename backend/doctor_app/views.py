from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hospital_app.serializers import HospitalSerializer
from doctor_app.serializers import ConsultationSerializer, DoctorSerializer, DoctorsBriefSerializer, QualificationSerializer, SpecialitySerializer
from hospital_app.models import Address, City, Hospital
from doctor_app.models import Doctor, Qualification, Speciality
from utils.common_methods import generate_serializer_error

# Create your views here.
class SpecialityView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        try:
            data = request.data
            if ("related_speciality_id" in data) and (data["related_speciality_id"] != (None or "")):
                related_speciality = Speciality.objects.get(
                    id=data["related_speciality_id"])
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
            serializer = DoctorsBriefSerializer(doctors, many=True)
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
            if "qualification_set" in data:
                for qual in data["qualification_set"]:
                    q_serializer = None
                    if "id" in qual:
                        qual_id = qual.get("id")
                        qualification = Qualification.objects.get(id=qual_id)
                        q_serializer = QualificationSerializer(
                            qualification, data=qual, partial=True)
                    else:
                        qual["doctor"] = doctor.id
                        q_serializer = QualificationSerializer(
                            data=qual, partial=True)
                    if not q_serializer.is_valid():
                        raise Exception(
                            generate_serializer_error(q_serializer.errors))
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

class GetDoctorDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            doctor = Doctor.objects.get(id=id)
            serializer = DoctorSerializer(doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchDoctors(APIView):
    def get(self, request):
        try:
            speciality = request.query_params['speciality'] if 'speciality' in request.query_params and request.query_params['speciality'] !="" else None
            hospital = request.query_params['hospital'] if 'hospital' in request.query_params and request.query_params['hospital'] !="" else None
            city = request.query_params['city'] if 'city' in request.query_params and request.query_params['city'] !="" else None
            area = request.query_params['area'] if 'area' in request.query_params and request.query_params['area'] !="" else None
            doctors = None
            if speciality != None:
                doctors = None
                if hospital == None:
                    if city == None:
                        doctors = Doctor.objects.filter(specialities=speciality)                        
                    else :
                        if area == None:
                            doctors = Doctor.objects.filter(specialities=speciality, hospitals__address__city=city).distinct()
                            # Added "distinct" here as sometimes it was returning same object multiple times.
                        else:
                            doctors = Doctor.objects.filter(specialities=speciality, hospitals__address__city=city, hospitals__address__area=area).distinct()

                else :
                    doctors = Doctor.objects.filter(specialities=speciality, hospitals=hospital)
            else :
                if hospital != None:
                    doctors = Doctor.objects.filter(hospitals=hospital)
                else:
                    if city != None:
                        if area == None:
                            doctors = Doctor.objects.filter(hospitals__address__city=city).distinct()
                            # Added "distinct" here as sometimes it was returning same object multiple times.
                        else:
                            doctors = Doctor.objects.filter(hospitals__address__city=city, hospitals__address__area=area).distinct()
            serializer = DoctorsBriefSerializer(doctors, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultationView(APIView):
    permission_classes = [IsAuthenticated]

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
