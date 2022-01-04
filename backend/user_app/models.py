import os
from django.db import models
from auth_app.models import TimeStampMixin, User
from doctor_app.models import Consultation, ConsultationSlot, Doctor, Speciality, Hospital
from hospital_app.models import Hospital, Address, AppointmentStatus
from enumchoicefield import ChoiceEnum, EnumChoiceField
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from django.conf import settings

# Create your models here.
class SubscriptionTypes(ChoiceEnum):
    GENERAL = 'general'
    PREMIUM = 'premium'
    GOLD = 'gold'

# We will have to manually create different schemes for different subscriptions and different validity
class SubscriptionScheme(TimeStampMixin):
    subscription_type = EnumChoiceField(SubscriptionTypes)
    validity = models.PositiveIntegerField()        #In days
    charges = models.FloatField()

class UserDetail(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=False,
    )
    dob = models.DateField()
    height = models.CharField(max_length=10)
    weight = models.FloatField()
    blood_group = models.CharField(max_length=10)
    image = models.TextField()

class UserSubscription(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(SubscriptionScheme, on_delete=models.SET_NULL, null=True)
    valid_from = models.DateField()
    valid_till = models.DateField()
    active = models.BooleanField(default=False)

class HealthCondition(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="health_condition_user"
    )
    condition = models.CharField(max_length=256)
    details = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="health_condition_added_by")

class HealthRecordTypes(ChoiceEnum):
    BLOOD_PRESSURE = "blood_pressure"
    SUGAR_LEVEl = "sugar_level"
    EYESIGNT = "eyesight"
    OTHER = "other"

class HealthRecord(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sugar_level_user"
    )
    type = EnumChoiceField(HealthRecordTypes)
    other_type_name = models.CharField(max_length=100, blank=True)
    value = HStoreField()
    details = models.TextField(blank=True)
    is_latest = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sugar_level_added_by")
    measured_by = models.CharField(max_length=100, blank=True)
    report_url = models.TextField(blank=True)

class AppointmentTypes(ChoiceEnum):
    FRESH = 'fresh'
    FOLLOWUP = 'follow_up'

class Appointment(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    # speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, blank=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.OneToOneField(ConsultationSlot, on_delete=models.SET_NULL, null=True, blank=True)
    status = EnumChoiceField(AppointmentStatus, default=AppointmentStatus.CREATED)
    status_update_remark = models.TextField(blank=True)
    appointment_type = EnumChoiceField(AppointmentTypes, default=AppointmentTypes.FRESH)
    original_appointment_ref = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # original_appointment_ref will be used incase of "followup appointments"

class Prescription(TimeStampMixin):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    # file_path = models.TextField()
    # We will use "file_path" field later to store path of stored file on AWS S3 bucket 
    file_path = models.FileField(blank=False, null=False, upload_to='prescriptions/%Y-%m-%d')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __unicode__(self):
        return '%s' % (self.file_path.name)
    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file_path.name))
        super(Prescription,self).delete(*args,**kwargs)

class PrescribedMedicine(TimeStampMixin):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    quantity = models.PositiveIntegerField()
    direction = models.CharField(max_length=256, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    # In notes doctor can write for what purpose the medicine is given etc.

class CommunicationTypes(ChoiceEnum):
     DOCTOR_AND_CONSULTATION_RELATED = 'doctor_and_consultation_related'
     HOSPITAL_RELATED = 'hospital_related'
     PATHLAB_RELATED = 'pathlab_related'
     HELP_SUPPORT = 'help_support'
     COMPLAINT = 'complaint'
     MEDICINE_PURCHASE_RELATED = 'purchased_medicine_related'

class Communication(TimeStampMixin):
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_from_user")
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_to_user")
    communication_type = EnumChoiceField(CommunicationTypes)
    
class CommunicationMute(TimeStampMixin):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE)
    muted_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="communication_muted_for")
    muted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_muted_by")

class CommunicationShare(TimeStampMixin):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="communication_share_with")
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_share_by")
    
class Message(TimeStampMixin):
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    files_path = ArrayField(models.TextField())

class FeedbackTypes(ChoiceEnum):
    COMMUNICATION = 'communication'
    CONSULTATION = 'consultation'
    HOSPITAL = 'hospital'
    HELP_AND_SUPPORT = 'help_and_support'
    APP_REVIEW = 'app_review'
    MEDICINE_PURCHASE = 'medicine_purchase'

class Feedback(TimeStampMixin):
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    type = EnumChoiceField(FeedbackTypes)
    reference_id = models.UUIDField(primary_key=False)
    # Here we have used UUIDField since it can be aything like Appointment_id, Doctor_id, Communication_id etc
    overall_rating = models.FloatField()
    subtype_ratings = models.JSONField()
    # subtype_ratings will have following fields - rating, remark 
    
