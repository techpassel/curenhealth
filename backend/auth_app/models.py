from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField

# Common class to be used wherever created_at and updated_at fields are required.
# We just have to extend it in the class where we want these fields and we don't have to define these fields again.
class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserType(ChoiceEnum):
    USER = 'user'
    USER_STAFF = 'user_staff'
    DOCTOR = 'doctor'
    DOCTOR_STAFF = 'doctor_staff'
    HOSPITAL = 'hospital'
    HOSPITAL_STAFF = 'hospital_staff'
    PATHLAB = 'pathlab'
    PATHLAB_STAFF = 'pathlab_staff'
    ADMIN = 'admin'
    ADMIN_STAFF = 'admin_staff'
    ADMIN_PHARMACY_STAFF = 'admin_pharmacy_staff'


# Create your models here.
class User(TimeStampMixin):
    class Meta:
        db_table = 'user'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=80, unique=True)
    country_code = models.CharField(max_length=11, default='+91')
    contact_num = models.BigIntegerField()
    password = models.CharField(max_length=256)
    usertype = EnumChoiceField(UserType, default=UserType.USER)

