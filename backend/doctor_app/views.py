from functools import partial
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from hospital_app.serializers import HospitalSerializer
from doctor_app.serializers import ConsultationDefalutTimingSerializer, ConsultationSerializer, ConsultationSlotSerializer, DoctorSerializer, DoctorsBriefSerializer, QualificationSerializer, SpecialitySerializer
from hospital_app.models import Address, City, Hospital, Weekday
from doctor_app.models import Consultation, ConsultationDefalutTiming, ConsultationSlot, Doctor, Qualification, Speciality, ConsultationType
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


class GetDoctorDetailsView(APIView):
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


class SearchDoctorsView(APIView):
    def get(self, request):
        try:
            speciality = request.query_params['speciality'] if 'speciality' in request.query_params and request.query_params['speciality'] != "" else None
            hospital = request.query_params['hospital'] if 'hospital' in request.query_params and request.query_params['hospital'] != "" else None
            city = request.query_params['city'] if 'city' in request.query_params and request.query_params['city'] != "" else None
            location = request.query_params['location'] if 'location' in request.query_params and request.query_params['location'] != "" else None
            doctors = None
            if speciality != None:
                doctors = None
                if hospital == None:
                    if city == None:
                        doctors = Doctor.objects.filter(
                            specialities=speciality)
                    else:
                        if location == None:
                            doctors = Doctor.objects.filter(
                                specialities=speciality, hospitals__address__city=city).distinct()
                            # Added "distinct" here as sometimes it was returning same object multiple times.
                        else:
                            doctors = Doctor.objects.filter(
                                specialities=speciality, hospitals__address__city=city, hospitals__address__location=location).distinct()

                else:
                    doctors = Doctor.objects.filter(
                        specialities=speciality, hospitals=hospital)
            else:
                if hospital != None:
                    doctors = Doctor.objects.filter(hospitals=hospital)
                else:
                    if city != None:
                        if location == None:
                            doctors = Doctor.objects.filter(
                                hospitals__address__city=city).distinct()
                            # Added "distinct" here as sometimes it was returning same object multiple times.
                        else:
                            doctors = Doctor.objects.filter(
                                hospitals__address__city=city, hospitals__address__location=location).distinct()
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
                data["hospital"] = hospital.id
            if "hospital_id" in data:
                del data["hospital_id"]
            if ("address_id" in data) and (data["address_id"] != (None or "")):
                address_id = data.get("address_id")
                address = Address.objects.get(id=address_id)
                data["address"] = address.id
            if "address_id" in data:
                del data["address_id"]
            serializer = ConsultationSerializer(data=data, partial=True)
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
            consultation = Consultation.objects.filter(id=id).first()
            if consultation == None:
                return Response("Consultation not found", status=status.HTTP_400_BAD_REQUEST)
            if ("hospital_id" in data) and (data["hospital_id"] != (None or "")):
                hospital_id = data.get("hospital_id")
                hospital = Hospital.objects.get(id=hospital_id)
                data["hospital"] = hospital.id
            if "hospital_id" in data:
                del data["hospital_id"]
            if ("address_id" in data) and (data["address_id"] != (None or "")):
                address_id = data.get("address_id")
                address = Address.objects.get(id=address_id)
                data["address"] = address.id
            if "address_id" in data:
                del data["address_id"]
            serializer = ConsultationSerializer(
                consultation, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchConsultationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            doctor_id = request.query_params['doctor'] if 'doctor' in request.query_params and request.query_params['doctor'] != "" else None
            consultation_type = request.query_params[
                'type'] if 'type' in request.query_params and request.query_params['type'] != "" else None
            consultations = None
            if consultation_type == None:
                consultations = Consultation.objects.filter(
                    doctor=doctor_id)
            else:
                ct = None
                # Method to get value of EnumChoiceFields to use in model objects.
                for r in ConsultationType:
                    if ConsultationType[consultation_type] == r:
                        ct = r
                consultations = Consultation.objects.filter(
                    doctor=doctor_id, consultation_type=ct)
            serializer = ConsultationSerializer(consultations, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultationDefaultTimingsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            consultation_id = data.get("consultation_id")
            consultation = Consultation.objects.filter(id=consultation_id).first()
            if consultation == None:
                return Response("Consultation not found", status=status.HTTP_400_BAD_REQUEST)
            data["consultation"] = consultation.id
            del data["consultation_id"]
            serializer = ConsultationDefalutTimingSerializer(data=data)
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
            consultation_timing = ConsultationDefalutTiming.objects.filter(id=id).first()
            if consultation_timing == None:
                return Response("Consultation not found", status=status.HTTP_400_BAD_REQUEST)
            serializer = ConsultationDefalutTimingSerializer(consultation_timing, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConsultationSlotsView(APIView):
    def post(self, request):
        try:
            data = request.data
            consultation_timing_id = data.get("consultation_timing_id")
            consultation_timing = ConsultationDefalutTiming.objects.filter(id=consultation_timing_id).first()
            if consultation_timing == None:
                return Response("Consultation timing not found", status=status.HTTP_400_BAD_REQUEST)
            data["consultation_timing"] = consultation_timing.id
            del data["consultation_timing_id"]
            serializer = ConsultationSlotSerializer(data=data)
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
            consultation_slot = ConsultationSlot.objects.filter(id=id).first()
            if consultation_slot == None:
                return Response("Consultation slot not found", status=status.HTTP_400_BAD_REQUEST)
            serializer = ConsultationSlotSerializer(consultation_slot, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetSlotsByConsultationTimingView(APIView):
    def get(self, request, consultation_timing_id):
        try:
            slots = ConsultationSlot.objects.filter(consultation_timing=consultation_timing_id)
            serializer = ConsultationSlotSerializer(slots, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)