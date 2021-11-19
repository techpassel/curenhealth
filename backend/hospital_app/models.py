from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from auth_app.models import TimeStampMixin, User
from enumchoicefield import ChoiceEnum, EnumChoiceField
from enum import Enum

# Create your models here.
class City(TimeStampMixin):
    name = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)


class Address(models.Model):
    city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=100)
    address = models.TextField()
    landmark = models.TextField()
    zipcode = models.IntegerField()
    country_std_code = models.CharField(max_length=11)
    phone = models.BigIntegerField()
    is_default = models.BooleanField(default=False)


class Weekday(ChoiceEnum):
    MONDAY = 'mon'
    TUESDAY = 'tues'
    WEDNESDAY = 'wed'
    THURSDAY = 'thurs'
    FRIDAY = 'fri'
    SATURDAY = 'satur'
    SUNDAY = 'sun'


class SlotPeriod(ChoiceEnum):
    AM = "am"
    PM = "pm"


class Hospital(TimeStampMixin):
    hospital_admin = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, primary_key=False)
    hospital_name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    contact_details = models.TextField(blank=True)
    additional_details = models.TextField(blank=True)


class Pathlab(TimeStampMixin):
    pathlab_admin = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, primary_key=False)
    pathlab_name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    contact_details = models.TextField(blank=True)
    additional_details = models.TextField(blank=True)


class CheckupPlanTypes(ChoiceEnum):
    FULL_BODY_CHECKUP = 'full_body_checkup'
    OTHER_TEST = 'other_test'
    CT_SCAN = 'ct_scan'
    # We will add more types later


class CheckupPlan(TimeStampMixin):
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, null=True, blank=True)
    pathlab = models.ForeignKey(
        Pathlab, on_delete=models.CASCADE, null=True, blank=True)
    type = EnumChoiceField(CheckupPlanTypes)
    home_sample_collection = models.BooleanField()
    timing = models.CharField(max_length=256)
    available_days = ArrayField(EnumChoiceField(Weekday))
    plan_name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    additional_details = models.TextField(blank=True)
    charges = models.FloatField()


class CheckupDefalutTiming(TimeStampMixin):
    checkup_plan = models.ForeignKey(CheckupPlan, on_delete=models.CASCADE)
    day_name = EnumChoiceField(Weekday)
    start_hour = models.PositiveIntegerField()
    start_minute = models.PositiveIntegerField()
    start_period = EnumChoiceField(SlotPeriod)
    end_hour = models.PositiveIntegerField()
    end_minute = models.PositiveIntegerField()
    end_period = EnumChoiceField(SlotPeriod)


class AppointmentStatus(ChoiceEnum):
    CREATED = 'created'
    CONFIRMED = 'confirmed'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'


def extend_enum(inherited_enum):
    def wrapper(added_enum):
        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)
    return wrapper


@extend_enum(AppointmentStatus)
class CheckupAppointmentStatus(ChoiceEnum):
    PROCESSING = 'processing'
    PENDING = 'pending'
    # Here we have inherited other status from 'AppointmentStatus'


class CheckupAppointment(TimeStampMixin):
    checkup_plan = models.ForeignKey(CheckupPlan, on_delete=models.PROTECT)
    desired_date = models.DateField()
    desired_time = models.CharField(max_length=256)
    # In case of decline please mention the reason and next available timing
    original_checkupappointment_ref = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="original_checkup_appointment_ref")
    sample_collection_time = models.DateTimeField()
    expected_delivery_date = models.DateField()
    actual_delivery_time = models.DateTimeField()


class CheckupStatus(TimeStampMixin):
    checkup_appointment = models.ForeignKey(
        CheckupAppointment, on_delete=models.CASCADE)
    status = EnumChoiceField(CheckupAppointmentStatus,
                             default=CheckupAppointmentStatus.CREATED)
    remark = models.CharField(max_length=256, blank=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)


class Checkupreports(TimeStampMixin):
    checkup_appointment = models.ForeignKey(
        CheckupAppointment, on_delete=models.CASCADE)
    files_paths = ArrayField(models.TextField())
    remark = models.TextField()
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
