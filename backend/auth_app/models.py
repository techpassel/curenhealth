from django.db import models
from enumchoicefield import ChoiceEnum, EnumChoiceField
import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

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
    HOSPITAL_ADMIN = 'hospital_admin'
    HOSPITAL_STAFF = 'hospital_staff'
    PATHLAB_ADMIN = 'pathlab_admin'
    PATHLAB_STAFF = 'pathlab_staff'
    SUPERADMIN = 'superadmin'
    SUPERADMIN_STAFF = 'superadmin_staff'
    SUPERADMIN_PHARMACY_STAFF = 'superadmin_pharmacy_staff'
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User`.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, email, first_name, last_name, phone, password, country_code="+91",
                    usertype=UserType.USER):
        if email is None:
            raise TypeError('Email is empty.')
        if password is None:
            raise TypeError('Password is empty.')
        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name,
                          phone=phone, country_code=country_code, usertype=usertype)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, phone, password, country_code="+91",
                         usertype=UserType.SUPERADMIN):

        user = self.create_user(email, first_name, last_name, phone, password, country_code, usertype)
        return user

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    class Meta:
        db_table = 'user'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True)
    country_code = models.CharField(max_length=11)
    phone = models.BigIntegerField()
    usertype = EnumChoiceField(UserType, default=UserType.USER)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        """
        return self.first_name+' '+self.last_name

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        """
        return self.last_name

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token


