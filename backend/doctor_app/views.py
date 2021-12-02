from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from auth_app.serializers import RegistrationSerializer
from auth_app.models import TokenType, User, UserType, VerificationToken
from user_app.serializers import UserSerializer
from utils.email import client_staff_activation_email, update_user_email
from doctor_app.serializers import ClientStaffSerializer, ConsultationSessionSerializer, ConsultationSerializer, ConsultationSlotSerializer, DoctorSerializer, DoctorsBriefSerializer, QualificationSerializer, SpecialitySerializer
from hospital_app.models import Address, Hospital
from doctor_app.models import ClientStaff, ClientStaffPermissions, Consultation, ConsultationSession, ConsultationSlot, Doctor, Qualification, Speciality, ConsultationType
from utils.common_methods import generate_serializer_error, get_client_staff_default_password, verify_clientstaff_permissions

# Create your views here.


class SpecialityView(APIView):
    permission_classes = [IsAuthenticated]

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
            consultation = Consultation.objects.filter(
                id=consultation_id).first()
            if consultation == None:
                return Response("Consultation not found", status=status.HTTP_400_BAD_REQUEST)
            data["consultation"] = consultation.id
            del data["consultation_id"]
            serializer = ConsultationSessionSerializer(data=data)
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
            consultation_session = ConsultationSession.objects.filter(
                id=id).first()
            if consultation_session == None:
                return Response("Consultation not found", status=status.HTTP_400_BAD_REQUEST)
            serializer = ConsultationSessionSerializer(
                consultation_session, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConsultationSlotsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            data = request.data
            consultation_session_id = data.get("consultation_session_id")
            consultation_session = ConsultationSession.objects.filter(
                id=consultation_session_id).first()
            if consultation_session == None:
                return Response("Consultation timing not found", status=status.HTTP_400_BAD_REQUEST)
            data["consultation_session"] = consultation_session.id
            del data["consultation_session_id"]
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
            serializer = ConsultationSlotSerializer(
                consultation_slot, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSlotsByConsultationTimingView(APIView):
    def get(self, request, consultation_session_id):
        try:
            slots = ConsultationSlot.objects.filter(
                consultation_session=consultation_session_id)
            serializer = ConsultationSlotSerializer(slots, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        created_user_id = None
        try:
            request_user = request.user
            request_user_type = request_user.usertype
            request_user_name = request_user.get_full_name()
            unit_type = None
            unit_name = None
            if request_user_type == UserType.DOCTOR or request_user_type == UserType.DOCTOR_STAFF:
                unit_type = "DOCTOR"
                if request_user_type == UserType.DOCTOR_STAFF:
                    requesting_staff = ClientStaff.objects.get(
                        user=request_user.id)
                    unit_name = requesting_staff.doctor_details.doctor_name
                else:
                    unit_name = request_user_name
            data = request.data
            unit_type = unit_type.title()
            unit_name = unit_name.title()
            request_user_name = request_user_name.title()
            # Calling this function to verify permissions sent by user belongs to ClientStaffPermissions
            # We are just calling this method as if any of the permission sent by user doesn't belong to ClientStaffPermissions
            # Then exception will be throw and response will be returned to him/her from except block.
            verify_clientstaff_permissions(data["permissions"])
            user = data.get("user")
            password = get_client_staff_default_password(unit_name)
            user["password"] = password
            user_serializer = RegistrationSerializer(data=user)
            if not user_serializer.is_valid():
                raise Exception(generate_serializer_error(
                    user_serializer.errors))
            user_serializer.save()

            created_user_id = user_serializer.data.get("id")
            doctor = Doctor.objects.filter(id=data.get("doctor_id")).first()
            if doctor == None:
                raise Exception("Doctor not found.")
            data["doctor"] = doctor.id
            del data["doctor_id"]
            data["user"] = user_serializer.data.get("id")
            serializer = ClientStaffSerializer(data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            client_staff_activation_email(
                user_serializer.data, password, request_user_name, unit_type, unit_name)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            if created_user_id != None:
                user = User.objects.get(id=created_user_id)
                user.delete()
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            request_user = request.user
            request_user_type = request_user.usertype
            request_user_name = request_user.get_full_name()
            unit_type = None
            unit_name = None
            if request_user_type == UserType.DOCTOR or request_user_type == UserType.DOCTOR_STAFF:
                unit_type = "DOCTOR"
                if request_user_type == UserType.DOCTOR_STAFF:
                    requesting_staff = ClientStaff.objects.get(
                        user=request_user.id)
                    unit_name = requesting_staff.doctor_details.doctor_name
                else:
                    unit_name = request_user_name
            unit_type = unit_type.title()
            unit_name = unit_name.title()
            request_user_name = request_user_name.title()
            data = request.data
            client_staff_id = data.get("id")
            client_staff_data = {}
            # Calling this function to verify permissions sent by user belongs to ClientStaffPermissions
            # We are just calling this method as if any of the permission sent by user doesn't belong to ClientStaffPermissions
            # Then exception will be throw and response will be returned to him/her from except block.
            verify_clientstaff_permissions(data["permissions"])
            # Updating User table data
            if "user" in data:
                user = data.get("user")
                user_id = user.get("id")
                user_details = User.objects.get(id=user_id)
                updated_email = None
                if "email" in user:
                    del user["email"]
                user_serializer = RegistrationSerializer(
                    user_details, data=user, partial=True)
                if not user_serializer.is_valid():
                    raise Exception(generate_serializer_error(user_serializer.errors))
                user_serializer.save()
            client_staff_data["user"] = user_serializer.data.get("id")
            # Now updating Client staff table data
            if "doctor_id" in data:
                doctor = Doctor.objects.get(id=data.get("doctor_id"))
                client_staff_data["doctor"] = doctor.id
            if "permissions" in data:
                client_staff_data["permissions"] = data.get("permissions")
            client_staff = ClientStaff.objects.get(id=client_staff_id)
            serializer = ClientStaffSerializer(
                client_staff, data=client_staff_data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateClientStaffEmail(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            request_user = request.user
            request_user_type = request_user.usertype
            request_user_name = request_user.get_full_name()
            unit_type = None
            unit_name = None
            if request_user_type == UserType.DOCTOR or request_user_type == UserType.DOCTOR_STAFF:
                unit_type = "DOCTOR"
                if request_user_type == UserType.DOCTOR_STAFF:
                    requesting_staff = ClientStaff.objects.get(
                        user=request_user.id)
                    unit_name = requesting_staff.doctor_details.doctor_name
                else:
                    unit_name = request_user_name
            unit_type = unit_type.title()
            unit_name = unit_name.title()
            request_user_name = request_user_name.title()
            password = get_client_staff_default_password(unit_name)
            data = request.data
            user_id = data.get("user_id")
            email = data.get("email")
            
            user_details = User.objects.get(id=user_id)
            msg = None
            if user_details.email == email:
                msg = "You provided same email as the previous one.Please provide a different email to update your staff's registered email."
            update_data = {"email": email}
            if msg == None:
                if user_details.is_email_verified:
                    update_user_email(user_details, data.get("email"), TokenType.CLIENT_STAFF_EMAIL_UPDATION_TOKEN)
                    msg = "Old email was already verified by user.So we have sent a verification email on the updated email address. When he verifies the email, his registered email will be automatically updated."
                else:
                    user_serializer = RegistrationSerializer(
                        user_details, data=update_data, partial=True)
                    if not user_serializer.is_valid():
                        raise Exception(generate_serializer_error(user_serializer.errors))
                    user_serializer.save()
                    client_staff_activation_email(
                        user_serializer.data, password, request_user_name, unit_type, unit_name)
                    msg = "Registered email is updated and a verification email has been sent to the updated email."
            return Response(msg, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendClientStaffVerificationEmail(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request_user = request.user
            request_user_type = request_user.usertype
            request_user_name = request_user.get_full_name()
            unit_type = None
            unit_name = None
            if request_user_type == UserType.DOCTOR or request_user_type == UserType.DOCTOR_STAFF:
                unit_type = "DOCTOR"
                if request_user_type == UserType.DOCTOR_STAFF:
                    requesting_staff = ClientStaff.objects.get(
                        user=request_user.id)
                    unit_name = requesting_staff.doctor_details.doctor_name
                else:
                    unit_name = request_user_name
            unit_type = unit_type.title()
            unit_name = unit_name.title()
            request_user_name = request_user_name.title()
            password = get_client_staff_default_password(unit_name)
            data = request.data
            user_id = data.get("user_id")
            user_details = User.objects.get(id=user_id)
            if user_details.is_email_verified:
                existing_verification_token = VerificationToken.objects.filter(user=user_id, token_type=TokenType.CLIENT_STAFF_EMAIL_UPDATION_TOKEN).first()
                update_user_email(user_details, existing_verification_token.updating_value, TokenType.CLIENT_STAFF_EMAIL_UPDATION_TOKEN)
            else:
                client_staff_activation_email(
                    user_details, password, request_user_name, unit_type, unit_name)
            return Response("Verification email resend successfully", status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)