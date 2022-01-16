from datetime import datetime, timedelta
from functools import partial
from django.contrib.auth import authenticate
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User, VerificationToken
from auth_app.serializers import RegistrationSerializer
from doctor_app.models import ConsultationSlot, SlotAvailablity
from doctor_app.serializers import ConsultationSlotSerializer
from hospital_app.models import AppointmentStatus
from utils.email import update_user_email
from user_app.serializers import AppointmentSerializer, CommunicationMessageSerializer, CommunicationSerializer, FeedbackSerializer, HealthRecordsSerializer, PrescribedMedicineSerializer, PrescriptionSerializer, SubscriptionSchemesSerializer, UserDetailsSerializer, UserSubscriptionSerializer
from user_app.models import Appointment, CommmunicationReferenceTypes, CommunicationTypes, Feedback, FeedbackTypes, HealthRecord, HealthRecordTypes, PrescribedMedicine, Prescription, PrescriptionDocument, SubscriptionScheme, UserDetail, UserSubscription
from utils.common_methods import generate_serializer_error
import pytz
from rest_framework.parsers import MultiPartParser, FormParser
# Create your views here.


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = request.query_params.get("limit")
            offset = request.query_params.get("offset")
            start_val = int(offset)
            end_val = int(offset) + int(limit)
            users = UserDetail.objects.all()[start_val:end_val]
            serializer = UserDetailsSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            data = request.data
            user_id = data.get("user_id")
            user = User.objects.get(id=user_id)
            if user.is_active == False:
                return Response("User is not active", status=status.HTTP_400_BAD_REQUEST)
            del data["user_id"]
            data["user"] = user.id
            serializer = UserDetailsSerializer(data=request.data)
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
            user_details = UserDetail.objects.filter(
                id=request.data.get("id")).first()
            if user_details == None:
                return Response("No Userdetails found with given id.", status=status.HTTP_400_BAD_REQUEST)
            serializer = UserDetailsSerializer(
                user_details, data=request.data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user_details = UserDetail.objects.get(user=user_id)
            serializer = UserDetailsSerializer(user_details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUserDetailsView(APIView):
    def delete(self, request, id):
        try:
            user_details = UserDetail.objects.filter(id=id).first()
            if user_details == None:
                return Response("No Userdetails found with given id.", status=status.HTTP_400_BAD_REQUEST)
            user_details.delete()
            return Response("Userdetails deleted successfully.", status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty", status=status.HTTP_400_BAD_REQUEST)
            restricted_items = ['email', 'password']
            for key in restricted_items:
                if key in user_data:
                    return Response(f"{key} can't be changed from this api.", status=status.HTTP_403_FORBIDDEN)
            user = User.objects.get(id=user_data['id'])
            serializer = RegistrationSerializer(
                user, data=user_data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError as err:
            err = err.args[0].split("DETAIL:  Key")
            err = ((err[1] if len(err) > 1 else err[0]).strip())
            return Response(err, status=status.HTTP_400_BAD_REQUEST)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            user_instance = User.objects.get(id=user_id)
            if user_instance == None:
                return Response("No User found with given id.", status=status.HTTP_400_BAD_REQUEST)
            user_instance.delete()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist as err:
            return Response("User not found.", status=status.HTTP_304_NOT_MODIFIED)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty", status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(id=user_data['id'])
            current_password = user_data['current_password']
            auth_user = authenticate(
                username=user.email, password=current_password)
            if auth_user is None:
                return Response("Your provided current password is incorrect. If you forget your password then please logout and click on 'forget password' link and follow instructions to reset your password.", status=status.HTTP_400_BAD_REQUEST)
            new_data = {"password": user_data["new_password"]}
            serializer = RegistrationSerializer(
                instance=user, data=new_data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEmailRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            user_data = request.data
            if 'id' not in user_data or user_data['id'] < 1:
                return Response("User id cannot be empty.", status=status.HTTP_400_BAD_REQUEST)
            email_user = User.objects.filter(
                email=user_data['new_email']).first()
            if email_user != None:
                return Response("New email you provided already exists.", status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.filter(id=user_data['id']).first()
            if user == None:
                return Response("User with given id not found", status=status.HTTP_400_BAD_REQUEST)
            if user.email != user_data['current_email']:
                return Response("Current email did not matched with your stored data.", status=status.HTTP_400_BAD_REQUEST)
            update_user_email(user, user_data["new_email"])

            return Response("A verification email is send to your updated email id. Please verify your email to link it with your account.", status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateEmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            response = ""
            verification_token_obj = VerificationToken.objects.filter(
                token=token).first()
            if(verification_token_obj == None):
                response = "Token is invalid or expired.Please try to update your email again."
            else:
                utc = pytz.UTC
                token_expiry_time = (
                    verification_token_obj.created_at + timedelta(hours=24)).replace(tzinfo=utc)
                current_time = datetime.now().replace(tzinfo=utc)
                if(token_expiry_time < current_time):
                    response = "Token is expired.Please try to update your email again."
                else:
                    new_email = verification_token_obj.updating_value
                    token_user = verification_token_obj.user
                    new_data = {"email": new_email}
                    serializer = RegistrationSerializer(
                        instance=token_user, data=new_data, partial=True)
                    if not serializer.is_valid():
                        raise Exception(
                            generate_serializer_error(serializer.errors))
                serializer.save()
                response = "Email updated successfully"
                verification_token_obj.delete()
            return Response(response, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = request.data
            other_type_name = data.other_type_name if "other_type_name" in data else ""
            type = HealthRecordTypes[data['type']]
            existing_latest = HealthRecord.objects.filter(
                user=data['user_id'], type=type, other_type_name=other_type_name, is_latest=True)
            islatest_data = {}
            islatest_data['is_latest'] = False
            for lat in existing_latest:
                serializer1 = HealthRecordsSerializer(
                    lat, data=islatest_data, partial=True)
                if not serializer1.is_valid():
                    raise Exception(
                        generate_serializer_error(serializer1.errors))
                serializer1.save()
            user = User.objects.filter(id=data['user_id']).first()
            if user == None:
                return Response("User not found", status=status.HTTP_400_BAD_REQUEST)
            data['user'] = user.id
            added_by = User.objects.filter(id=data['added_by']).first()
            if added_by == None:
                return Response("'added_by' user not found", status=status.HTTP_400_BAD_REQUEST)
            data['added_by'] = added_by.id
            serializer = HealthRecordsSerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            health_records = HealthRecord.objects.filter(
                id=request.data.get("id")).first()
            if health_records == None:
                return Response("Health Record not found", status=status.HTTP_400_BAD_REQUEST)
            serializer = HealthRecordsSerializer(
                health_records, data=request.data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetHealthRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            health_records = HealthRecord.objects.filter(user=user_id)
            serializer = HealthRecordsSerializer(health_records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteHealthRecordsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            health_record = HealthRecord.objects.filter(id=id).first()
            if health_record == None:
                return Response("Health Record not found", status=status.HTTP_400_BAD_REQUEST)
            health_record.delete()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllSubscriptionSchemesView(APIView):
    # It's create,Update and Delete APIs are created in admin_app as only admin can perform those actions
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            subscription_schemes = SubscriptionScheme.objects.all()
            serializer = SubscriptionSchemesSerializer(
                subscription_schemes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            user_id = data.get("user_id")
            user = User.objects.get(id=user_id)
            del data["user_id"]
            data["user"] = user.id
            # We will check if any other subscription is active. If yes then we won't activate it currently
            # Otherwise we will activate it.
            active_subscriptions = UserSubscription.objects.filter(
                user=user_id, active=True)
            if "active" in data and data["active"] == True:
                data["valid_from"] = datetime.today().date()
                for i in range(len(active_subscriptions)):
                    serializer1 = UserSubscriptionSerializer(active_subscriptions[i], data={
                                                             "active": False}, partial=True)
                    if not serializer1.is_valid():
                        raise Exception(
                            generate_serializer_error(serializer1.errors))
                    serializer1.save()
            else:
                if len(active_subscriptions) == 0:
                    data["active"] = True
                    data["valid_from"] = datetime.today().date()
                else:
                    data["active"] = False
                    data["valid_from"] = active_subscriptions[0]["valid_till"] + \
                        timedelta(days=1)

            subscription_scheme_id = data.get("subscription")
            subscription_scheme = SubscriptionScheme.objects.get(
                id=subscription_scheme_id)
            subscription_validity = subscription_scheme.validity
            data["valid_till"] = data["valid_from"] + \
                timedelta(days=subscription_validity)
            serializer = UserSubscriptionSerializer(data=data)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActivateUserSubscription(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            id = request.data.get("id")
            user_subscription = UserSubscription.objects.get(id=id)
            user_id = user_subscription.user.id
            if user_id != request.data.get("user_id"):
                raise Exception("User information is incorrect.")
            subscription_scheme_id = user_subscription.subscription.id
            subscription_scheme = SubscriptionScheme.objects.get(
                id=subscription_scheme_id)
            subscription_validity = subscription_scheme.validity
            active_subscriptions = UserSubscription.objects.filter(
                user=user_id, active=True)
            valid_from = datetime.today().date()
            valid_till = valid_from + timedelta(days=subscription_validity)
            serializer = UserSubscriptionSerializer(user_subscription, data={
                                                    "valid_from": valid_from, "valid_till": valid_till, "active": True}, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            # Deactivating all previously activated user-subscriptions
            active_subscriptions = UserSubscription.objects.filter(
                user=user_id, active=True).exclude(id=id)
            for i in range(len(active_subscriptions)):
                serializer1 = UserSubscriptionSerializer(active_subscriptions[i], data={
                                                         "active": False}, partial=True)
                if not serializer1.is_valid():
                    raise Exception(
                        generate_serializer_error(serializer1.errors))
                serializer1.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserSubscriptionDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user_subscription = UserSubscription.objects.get(id=id)
            serializer = UserSubscriptionSerializer(user_subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUsersAllSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user_subscription = UserSubscription.objects.filter(user=user_id)
            serializer = UserSubscriptionSerializer(
                user_subscription, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = AppointmentSerializer(data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            # While creating an appointments we need to update the status of slot also.
            slot_id = data.get('slot')
            slot = ConsultationSlot.objects.get(id=slot_id)
            slot_serializer = ConsultationSlotSerializer(
                slot, data={"availablity": SlotAvailablity.BOOKED}, partial=True)
            if not slot_serializer.is_valid():
                raise Exception(generate_serializer_error(
                    slot_serializer.errors))
            slot_serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            data = request.data
            appointment_id = data.get("id")
            # When a doctor or doctor_staff update the AppointmentStatus to "Declined" or "Cancelled".
            # Ask him/her whether to make appointment slot available again for other users or make it cancelled.
            make_slot_available = data.get(
                "make_slot_available") if "make_slot_available" in data else False
            appointment = Appointment.objects.filter(id=appointment_id).first()
            if appointment == None:
                return Response("Appointment not found", status=status.HTTP_400_BAD_REQUEST)
            serializer = AppointmentSerializer(
                appointment, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            # While updating status of appointments we need to update the status of slot also.
            if "status" in data:
                appointment_status = AppointmentStatus[data.get('status')]
                if appointment_status == AppointmentStatus.DECLINED or appointment_status == AppointmentStatus.CANCELLED:
                    slot_id = serializer.data.get('slot')
                    slot = ConsultationSlot.objects.get(id=slot_id)
                    availablity = SlotAvailablity.AVAILABLE if make_slot_available == True else SlotAvailablity.CANCELLED
                    slot_serializer = ConsultationSlotSerializer(
                        slot, data={"availablity": availablity}, partial=True)
                    if not slot_serializer.is_valid():
                        raise Exception(generate_serializer_error(
                            slot_serializer.errors))
                    slot_serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAppointmentsByDoctorView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doctor_id):
        try:
            appointments = Appointment.objects.filter(doctor=doctor_id)
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAppointmentsByUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            appointments = Appointment.objects.filter(user=user_id)
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            # Only user can delete his/her appointment and that also only when appointment status is Created.
            # Once Doctor, DoctorStaff or HospitalStaff updated the status to "Confirmed","Declined", etc.
            # He/she won't be able to delete it.However he will have option to cancel it.
            appointment = Appointment.objects.get(id=id)
            if appointment.status == AppointmentStatus.CREATED:
                slot_id = appointment.slot.id
                appointment.delete()
                slot = ConsultationSlot.objects.get(id=slot_id)
                slot_serializer = ConsultationSlotSerializer(
                    slot, data={"availablity": SlotAvailablity.AVAILABLE}, partial=True)
                if not slot_serializer.is_valid():
                    raise Exception(generate_serializer_error(
                        slot_serializer.errors))
                slot_serializer.save()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PrescriptionView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            documents = request.FILES.getlist('files', None)
            data = request.data
            del data["files"]
            prescription_serializer = PrescriptionSerializer(data=data, context={'documents': documents}, partial=True)
            if prescription_serializer.is_valid():
                prescription_serializer.save()
            return Response(prescription_serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPrescriptionsByAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            prescriptions = Prescription.objects.filter(appointment=appointment_id)
            prescription_serializer = PrescriptionSerializer(prescriptions, many=True)
            return Response(prescription_serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeletePrescriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            prescription = Prescription.objects.filter(id=id).first()
            if prescription == None:
                return Response("Prescription not found", status=status.HTTP_400_BAD_REQUEST)
            prescription.delete()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# This API will be used to delete a single document of the prescription
# If you want to delete entire prescription then call above API DeletePrescriptionView
class DeletePrescriptionDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            prescription_doc = PrescriptionDocument.objects.filter(id=id).first()
            if prescription_doc == None:
                return Response("Prescription document not found", status=status.HTTP_400_BAD_REQUEST)
            prescription_doc.delete()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PrescribedMedicineView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = PrescribedMedicineSerializer(data=data, partial=True)
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
            prescribed_medicine = PrescribedMedicine.objects.filter(pk=id).first()
            if prescribed_medicine == None:
                return Response("Prescribed medicine not found.", status=status.HTTP_400_BAD_REQUEST)
            
            serializer = PrescribedMedicineSerializer(prescribed_medicine, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data ,status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPrescribedMedicineByAppointmentIdView(APIView):
    permisssion_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        try:
            prescribed_medicines = PrescribedMedicine.objects.filter(appointment=appointment_id)
            prescription_medicine_serializer = PrescribedMedicineSerializer(prescribed_medicines, many=True)
            return Response(prescription_medicine_serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeletePrescribedMedicineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            prescribed_medicine = PrescribedMedicine.objects.filter(id=id).first()
            if prescribed_medicine == None:
                return Response("Prescribed medicine not found.", status=status.HTTP_200_OK)
            prescribed_medicine.delete()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            serializer = FeedbackSerializer(data=data)
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
            feedback = Feedback.objects.filter(pk = id).first()
            if feedback == None:
                return Response("Feedback not found.", status=status.HTTP_400_BAD_REQUEST)
            serializer = FeedbackSerializer(feedback, data=data, partial=True)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Feedback will never be searched by its id, iT will be searched based on Doctor_id, Consultation_id etc.
# So we will pass 2 parameters as query param with request URL - 
# 1. "type" - like "CONSULTATION" if we want to search for consultation id
# 2. "reference_id" - the actual consultation id value like 1 if we want to seach for all feedbacks for consultation_id 1. 
class GetFeedbackByReferenceId(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            reference_id = request.query_params.get('reference_id')
            type = request.query_params.get('type')
            type_val = None
            # Method to get value of EnumChoiceFields to use in model objects.Simple text value will thorw error.
            for t in FeedbackTypes:
                if FeedbackTypes[type] == t:
                    type_val = t
            feedbacks = Feedback.objects.filter(type=type_val, reference_id=reference_id)
            serializer = FeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteFeedback(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            feedback = Feedback.objects.filter(pk=id).first()
            if feedback == None:
                return Response("Feedback not found.", status=status.HTTP_400_BAD_REQUEST)
            feedback.delete()
            return Response(status=status.HTTP_200_OK)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommunicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            from_user = data.get('from_user') if 'from_user' in data else None
            communication_id = data.get('communication_id') if 'communication_type' in data and data.get('communication_type') != (None or '' or 0) else None
            if communication_id == None:
                # It means new communication is initiated.So we must have communication_type and from_user information and optional to_user.
                # to_user is optional as in case of HELP_SUPPORT, COMPLAINT and MEDICINE_PURCHASE_RELATED communications to_user will be added later.
                to_user = data.get('to_user') if 'to_user' in data else None
                communication_type = data.get('communication_type') if 'communication_type' in data else CommunicationTypes.GENERAL                
                if communication_type == CommunicationTypes.GENERAL and to_user == None:
                    return Response("to_user information is required", status=status.HTTP_400_BAD_REQUEST)
                
                reference_type = data.get('reference_type') if 'reference_type' in data else CommmunicationReferenceTypes.NONE
                reference_id = data.get('reference_id') if 'reference_id' in data else None
                communication_data = {'from_user': from_user, 'to_user': to_user, 'communication_type': communication_type, 'reference_type': reference_type, 'reference_id': reference_id}
                communication_serializer = CommunicationSerializer(data=communication_data)
                if not communication_serializer.is_valid():
                    raise Exception(generate_serializer_error(communication_serializer.errors))
                communication_serializer.save()
                communication_id = communication_serializer.data.get("id")
            # Following code is now common for new communication as well as new message in some existing communication 
            documents = request.FILES.getlist('files', None)
            message_data = {"communication": communication_id, "text": data.get("text"), "from_user": from_user}
            serializer = CommunicationMessageSerializer(data=message_data, context={'documents': documents},)
            if not serializer.is_valid():
                raise Exception(generate_serializer_error(serializer.errors))
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (AssertionError, Exception) as err:
            return Response(str(err), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response("Some error occured, please try again.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)