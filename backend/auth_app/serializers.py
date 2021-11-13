from rest_framework import serializers
from enumchoicefield import EnumChoiceField
from .models import User, UserType, VerificationToken
from django.contrib.auth import authenticate

class RegistrationSerializer(serializers.ModelSerializer):
    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    email = serializers.EmailField(max_length=256)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    country_code = serializers.CharField(max_length=11, required=False)
    phone = serializers.IntegerField()
    usertype = EnumChoiceField(UserType)
    is_active = serializers.BooleanField(required=False)
    is_email_verified = serializers.BooleanField(required=False)
    is_phone_verified = serializers.BooleanField(required=False)

    def create(self, validated_data):
        # Use the `create_user` method we wrote in User model(actually in UserManager) to create a new user.
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.country_code = validated_data.get(
            'country_code', instance.country_code)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.usertype = validated_data.get('usertype', instance.usertype)
        instance.is_active = validated_data.get(
            'is_active', instance.is_active)
        instance.is_email_verified = validated_data.get(
            'is_email_verified', instance.is_email_verified)
        instance.is_phone_verified = validated_data.get(
            'is_phone_verified', instance.is_phone_verified)
        password = validated_data.get('password', None)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request or response
        fields = ('id', 'email', 'first_name', 'last_name', 'country_code', 'phone',
                  'usertype', 'password', 'is_active', 'is_email_verified', 'is_phone_verified')
        # If you want to include all fields then you can define it as follows also.
        # fields = ('__all__')


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    country_code = serializers.CharField(max_length=11, required=False)
    phone = serializers.IntegerField(required=False)
    usertype = EnumChoiceField(UserType)
    token = serializers.CharField(max_length=255, read_only=True)
    is_email_verified = serializers.BooleanField(required=False)
    is_phone_verified = serializers.BooleanField(required=False)

    def validate(self, data):

        email = data.get('email', None)
        password = data.get('password', None)

        # Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # Raise an exception if a
        # password cis not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value since in our User
        # model we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)
        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'User with given email and password not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user is deactivated.'
            )
        return user

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request or response
        fields = ('id', 'email', 'first_name', 'last_name', 'country_code', 'phone',
                  'usertype', 'password', 'token', 'is_email_verified', 'is_phone_verified')
        # If you want to include all fields then you can define it as follows also.
        # fields = ('__all__')

class VerificationTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model= VerificationToken
        fields = ('id', 'user', 'token_type', 'token', 'updating_value')
