from django.db import models
from auth_app.models import TimeStampMixin, User
from doctor_app.models import Consultation, ConsultationSlot, Doctor, Speciality, Hospital
from hospital_app.models import Hospital, Address, AppointmentStatus
from enumchoicefield import ChoiceEnum, EnumChoiceField
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class SubscriptionTypes(ChoiceEnum):
    GENERAL = 'general'
    PREMIUM = 'premium'
    GOLD = 'gold'

# We will have to manually create different schemes for different subscriptions and different validity
class SubscriptionSchemes(TimeStampMixin):
    subscription_type = EnumChoiceField(SubscriptionTypes)
    days = models.PositiveIntegerField()
    charges = models.PositiveIntegerField()

class UserDetails(models.Model):
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

class UserSubscriptions(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(SubscriptionSchemes, on_delete=models.SET_NULL, null=True)
    valid_from = models.DateField()
    valid_till = models.DateField()
    active = models.BooleanField(default=True)

class HealthConditions(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="health_condition_user"
    )
    condition = models.CharField(max_length=256)
    details = models.TextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="health_condition_added_by")

class BloodPressure(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blood_pressure_user"
    )
    up_value = models.IntegerField()
    down_value = models.IntegerField()
    is_latest = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blood_pressure_added_by")
    measured_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blood_pressure_measured_by")

class SugarLevel(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sugar_level_user"
    )
    value = models.IntegerField()
    is_latest = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sugar_level_added_by")
    measured_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sugar_level_measured_by")

class EyeSight(TimeStampMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="eye_sight_user"
    )
    eyesight_value = models.IntegerField(null=True, blank=True)
    power_glass_value = models.CharField(max_length=100, blank=True)
    is_latest = models.BooleanField(default=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="eye_sight_added_by")
    measured_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="eye_sight_measured_by")

class AppointmentType(ChoiceEnum):
    FRESH = 'fresh'
    FOLLOWUP = 'follow_up'

class Appointment(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.SET_NULL, null=True, blank=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.SET_NULL, null=True, blank=True)
    slot = models.OneToOneField(ConsultationSlot, on_delete=models.SET_NULL, null=True, blank=True)
    status = EnumChoiceField(AppointmentStatus, default=AppointmentStatus.CREATED)
    status_update_remark = models.TextField()
    appointment_type = EnumChoiceField(AppointmentType, default=AppointmentType.FRESH)
    original_appointment_ref = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    # original_appointment_ref will be used incase of "followup appointments"

class Prescription(TimeStampMixin):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    file_path = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class PrescribedMedicine(TimeStampMixin):
    name = models.CharField(max_length=256)
    quantity = models.PositiveIntegerField()
    direction = models.CharField(max_length=256, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    # In notes doctor can write for what purpose this medicine is given etc.

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

class OfferOn(ChoiceEnum):
    IN_HOUSE_CONSULTATION = 'in_house_consultation'
    ONLINE_CONSULTATION = 'online_consultation'
    GENERAL_SUBSCRIPTION = 'general_subscription'
    PREMIUM_SUBSCRIPTION = 'premium_subscription'
    GOLD_SUBSCRIPTION = 'gold_subscription'
    MEDICINE = 'medicine'
    CLIENT_JOINING = 'client_joining'
    CLIENT_MEMBERSHIP_RENEWAL = 'client_membership_renewal'
    ALL = 'all'
    SPECIFIC = 'specific'

class OfferFor(ChoiceEnum):
    GENERAL_CUSTOMER = 'general_customer'
    PREMIUM_CUSTOMER = 'premium_customer'
    GOLD_CUSTOMER = 'gold_customer'
    DOCTOR = 'doctor'
    HOSPITAL = 'hospital'
    PATHLAB = 'pathlab'
    ADMIN_STAFF = 'admin_staff'
    ALL = 'all'
    SPECIFIC = 'specific'

class DiscountType(ChoiceEnum):
    IN_RUPEE = "in_rupee"
    IN_PERCENTAGE = "in_percentage"

class Coupon(TimeStampMixin):
    coupon_code = models.CharField(max_length=50)
    offer_on = ArrayField(EnumChoiceField(OfferOn))
    offer_for = ArrayField(EnumChoiceField(OfferFor))
    discount = models.PositiveIntegerField()
    discount_type = EnumChoiceField(DiscountType)
    minimun_spent_amount = models.PositiveIntegerField()
    specific_users = models.ManyToManyField(User, related_name="assigned_users")
    # We will use specific_users field if we want to create coupon for some specific user 
    # like in compensastion for some mistake or as reward for some achievement etc.
    valid_till = models.DateTimeField()
    