from rest_framework import serializers
from enumchoicefield import EnumChoiceField

from auth_app.models import User, UserType
from hospital_app.serializers import AddressSerializer
from .models import UserDetails


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = ['user', 'dob', 'height', 'weight',
                  'blood_group', 'image']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True, 
        required=False
    )

    email = serializers.EmailField(max_length=256, required=False)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    country_code = serializers.CharField(max_length=11, required=False)
    phone = serializers.IntegerField(required=False)
    # usertype = EnumChoiceField(UserType)
    is_email_verified = serializers.BooleanField(required=False)
    is_phone_verified = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'country_code',
                  'phone', 'password', 'is_email_verified', 'is_phone_verified')

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.country_code = validated_data.get(
            'country_code', instance.country_code)
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