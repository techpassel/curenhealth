import os
from django.db import models
from auth_app.models import TimeStampMixin, User
from doctor_app.models import Consultation, ConsultationSlot, Doctor, Speciality, Hospital
from hospital_app.models import Hospital, Address, AppointmentStatus
from enumchoicefield import ChoiceEnum, EnumChoiceField
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField
from django.conf import settings
import uuid
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
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # We don't need to delete PrescriptionDocument as models.CASCADE is applied in it for prescription
    # i.e whenever we will delete Prescription from database PrescriptionDocument will automatically be deleted from database
    # But in that case delete method of PrescriptionDocument won't be called and hence uploaded documents 
    # won't be deleted from the "uploads" folder.So we need to manually delete uploaded documents.Following code is for that purpose only.
    def delete(self, *args, **kwargs):
        documents = PrescriptionDocument.objects.filter(prescription=self.pk) 
        for doc in documents:
            os.remove(os.path.join(settings.MEDIA_ROOT, doc.document.name))
        super(Prescription,self).delete(*args,**kwargs)

# This model doesn't have any significance on its own.
# It is created just to enable multiple documents upload feature in Prescription model.
class PrescriptionDocument(TimeStampMixin):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="prescription_related_document")
    document = models.FileField(blank=False, null=False, upload_to='prescription/%Y-%m-%d')
    def __unicode__(self):
        return '%s' % (self.document.name)

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.document.name))
        super(PrescriptionDocument, self).delete(*args,**kwargs)

class PrescribedMedicine(TimeStampMixin):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    quantity = models.PositiveIntegerField()
    direction_of_use = models.CharField(max_length=256, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    # In notes doctor can write for what purpose the medicine is prescribed etc.

class CommmunicationReferenceTypes(ChoiceEnum): 
    NONE = 'none'
    DOCTOR_RELATED = 'doctor_related'
    CONSULTATION_RELATED = 'consultation_related'
    HOSPITAL_RELATED = 'hospital_related'
    PATHLAB_RELATED = 'pathlab_related'

class CommunicationTypes(ChoiceEnum):
    GENERAL = 'general'
    HELP_SUPPORT = 'help_support'
    COMPLAINT = 'complaint'
    MEDICINE_PURCHASE_RELATED = 'purchased_medicine_related'

class Communication(TimeStampMixin):
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_from_user")
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_to_user")
    communication_type = EnumChoiceField(CommunicationTypes, default=CommunicationTypes.GENERAL)
    reference_type = EnumChoiceField(CommmunicationReferenceTypes, default = CommmunicationReferenceTypes.NONE)
    reference_id = models.IntegerField()
    # reference_type and reference_id fields should be used to give reference.For example suppose we want to consult a doctor regarding a consultation then 
    # communication_type will be "General", reference_type will be "CONSULTATION_RELATED" and reference_id will be the reference id of the consultation regarding which we wanted to communicate with the doctor 
    # And if we want to consulta with the doctor regarding if he/she will be consultaing next day or not then in such case again consultation type will be General, reference_type will be None and reference _id will also be none 

class CommunicationMute(TimeStampMixin):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE)
    muted_for = models.ForeignKey(User, on_delete=models.CASCADE, related_name="communication_muted_for")
    muted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_muted_by")

class CommunicationShare(TimeStampMixin):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name="communication_shared_with")
    shared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="communication_shared_by")
    
class CommunicationMessage(TimeStampMixin):
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE, related_name="message_communication")
    text = models.TextField()
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    # We don't need to delete CommunicationMessageDocument as models.CASCADE is applied in it for CommunicationMessage
    # i.e whenever we will delete CommunicationMessage from database CommunicationMessageDocument will automatically be deleted from database
    # But in that case delete method of CommunicationMessageDocument won't be called and hence uploaded documents 
    # won't be deleted from the "uploads" folder.So we need to manually delete uploaded documents.Following code is for that purpose only.
    def delete(self, *args, **kwargs):
        documents = CommunicationMessageDocument.objects.filter(communication_message=self.pk) 
        for doc in documents:
            os.remove(os.path.join(settings.MEDIA_ROOT, doc.document.name))
        super(CommunicationMessage,self).delete(*args,**kwargs)

# This model doesn't have any significance on its own.
# It is created just to enable multiple documents upload feature in CommunicationMessage model.
class CommunicationMessageDocument(TimeStampMixin):
    communication_message = models.ForeignKey(CommunicationMessage, on_delete=models.CASCADE, related_name="communication_related_document")
    document = models.FileField(blank=False, null=False, upload_to='communication/%Y-%m-%d')
    def __unicode__(self):
        return '%s' % (self.document.name)

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.document.name))
        super(CommunicationMessageDocument, self).delete(*args,**kwargs)

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
    reference_id = models.IntegerField()
    # Here we have used integer field instead of foreign key since it can be aything among Appointment_id, Doctor_id, Communication_id, Consultation_id etc
    feedback = models.TextField(blank=True)
    overall_rating = models.IntegerField()
    subtype_ratings = models.JSONField()
    # subtype_ratings will have following fields - type, rating, remark 
    
