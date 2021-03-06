from django.db import models
from django.db.models.deletion import CASCADE
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
    ADMIN = 'superadmin'
    ADMIN_STAFF = 'superadmin_staff'
    ADMIN_PHARMACY_STAFF = 'superadmin_pharmacy_staff'
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

    def create_user(self, email, first_name, last_name, phone, password, country_std_code="+91",
                    usertype=UserType.USER):
        if email is None:
            raise TypeError('Email is empty.')
        if password is None:
            raise TypeError('Password is empty.')
        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name,
                          phone=phone, country_std_code=country_std_code, usertype=usertype)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, phone, password, country_std_code="+91",
                         usertype=UserType.ADMIN):

        user = self.create_user(email, first_name, last_name, phone, password, country_std_code, usertype)
        return user

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):
    # class Meta:
    #     db_table = 'user'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(db_index=True, unique=True)
    country_std_code = models.CharField(max_length=11)
    phone = models.BigIntegerField()
    usertype = EnumChoiceField(UserType, default=UserType.USER)
    is_active = models.BooleanField(default=False)
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
        return self.first_name

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

class TokenType(ChoiceEnum):
    SIGNUP_EMAIL_VERIFICATION_TOKEN = "signup_email_verification_token"
    UPDATE_EMAIL_VERIFICATION_TOKEN = "update_email_verification_token"
    RESET_PASSWORD_TOKEN = "reset_password_token"
    CLIENT_STAFF_VERIFICATION_TOKEN = "client_staff_verification_token"
    CLIENT_STAFF_EMAIL_UPDATION_TOKEN = "client_staff_email_updation_token"

class VerificationToken(TimeStampMixin):
    user = models.ForeignKey(User, on_delete=CASCADE)
    token_type = EnumChoiceField(TokenType, max_length=100)
    token = models.CharField(max_length=100, unique=True)
    updating_value = models.CharField(max_length=100)