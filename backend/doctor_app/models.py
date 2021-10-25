from datetime import date
from django.db import models
from auth_app.models import TimeStampMixin, User
from hospital_app.models import Hospital, Weekday, SlotPeriod, Address
from enumchoicefield import ChoiceEnum, EnumChoiceField
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Speciality(TimeStampMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    relates_speciality = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True)

class Qualification(models.Model):
    degree = models.CharField(max_length=256)
    institute = models.CharField(max_length=256)
    passing_year = models.IntegerField()
    remark = models.TextField()

class Doctor(TimeStampMixin):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    dob = models.DateField()
    image = models.TextField()
    practicing_year = models.IntegerField()
    specialitities = models.ManyToManyField(Speciality)
    hospitals = models.ManyToManyField(Hospital)
    qualifications = models.ForeignKey(Qualification, on_delete=models.SET_NULL, null=True, blank=True)
    details = models.TextField(blank=True)
    additional_details = models.TextField(blank=True)

class ConsultationType(ChoiceEnum):
    ONLINE = 'online'
    IN_HOUSE = 'in_house'

class Consultation(TimeStampMixin):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="consultation_doctor")
    consultation_type = EnumChoiceField(ConsultationType)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name="consultation_hospital")
    location = models.TextField()
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="consultation_address")
    charge = models.FloatField()
    remark = models.TextField()
    slot_duration = models.IntegerField()
    # It can be used in cases like if doctor want to mention if he see only followup patients in this consultation.

class ConsultationDefalutTiming(TimeStampMixin):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    day_name = EnumChoiceField(Weekday)
    start_hour = models.PositiveIntegerField()
    start_minute = models.PositiveIntegerField()
    start_period = EnumChoiceField(SlotPeriod)
    end_hour = models.PositiveIntegerField()
    end_minute = models.PositiveIntegerField()
    end_period = EnumChoiceField(SlotPeriod)

class SlotAvailablity(ChoiceEnum):
    AVAILABLE = 'available'
    BOOKED = 'booked'
    CANCELLED = 'cancelled'

class ConsultationSlot(TimeStampMixin):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    date = models.DateField()
    slots = models.CharField(max_length=15)
    availablity = EnumChoiceField(SlotAvailablity)
    # We will store slot value inthe form of "00:30AM", "04:45PM" etc.(minutes in multiple of consultation's slot_duration).
    # We will run cron job every sunday night and auto set ConsultationSlot based on ConsultationDefalutTiming and consultation's slot_duration.
    # We will do it in such a way that user users can see slot availablity for next 4 weeks. 
    
class ClientStaffRoles(ChoiceEnum):
    DOCTOR_STAFF = 'doctor_staff'
    HOSPITAL_STAFF = 'hospital_staff'
    PATHLAB_STAFF = 'pathlab_staff'

class ClientStaffPermissions(ChoiceEnum):
    HANDLE_APPOINTMENT = 'handle_appointment'
    HANDLE_CONSULTATION = 'handle_consultation'
    HANDLE_COMMUNICATION = 'handle_communication'
    MANAGE_OTHER_STAFF = 'handle_other_staff'
    MANAGE_PRESCRIPTION = 'manage_prescription'
    MANAGE_TEST_RESULTS = 'manage_test_results'
    MANAGE_CHECKUP_PLANS = 'manage_checkup_plans'
    HANDLE_CHECKUPS = 'handle_checkups'

class ClientStaff(TimeStampMixin):
    # Ex - Doctor_Staff, Hospital Staff, Pathlab Staff
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_staff_user")
    primary_role = EnumChoiceField(ClientStaffRoles) 
    doctor_id = models.ForeignKey(Doctor, on_delete=models.PROTECT, null=True, blank=True, related_name="client_staff_doctor")
    hospital_id = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name="client_staff_hospital")
    responsibilities = ArrayField(EnumChoiceField(ClientStaffPermissions))

class ClientStaffSecondaryRoles(TimeStampMixin):
    staff = models.ForeignKey(ClientStaff, on_delete=models.CASCADE, related_name="cs_secondary_role_user")
    secondary_role = EnumChoiceField(ClientStaffRoles)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.PROTECT, null=True, blank=True, related_name="cs_secondary_role_doctor")
    hospital_id = models.ForeignKey(Hospital, on_delete=models.PROTECT, null=True, blank=True, related_name="cs_secondary_role_hospital")
    responsibilities = ArrayField(EnumChoiceField(ClientStaffPermissions))