from django.db.models import fields
from rest_framework import serializers
from enumchoicefield import EnumChoiceField
from auth_app.models import User
from .models import Appointment, HealthRecord, HealthRecordTypes, Prescription, SubscriptionScheme, UserDetail, UserSubscription

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class UserDetailsSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    class Meta:
        model = UserDetail
        fields = ['id', 'user', 'user_details', 'dob', 'height', 'weight',
                  'blood_group', 'image']


class HealthRecordsSerializer(serializers.ModelSerializer):
    added_by_name = serializers.CharField(read_only=True, source="added_by.get_full_name")
    type = EnumChoiceField(HealthRecordTypes)

    class Meta:
        model = HealthRecord
        fields = ['id', 'user', 'type', 'other_type_name', 'value', 'details', 'is_latest',
                  'added_by', 'added_by_name', 'measured_by', 'report_url', 'created_at', 'updated_at']


class SubscriptionSchemesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionScheme
        fields = ['id', 'subscription_type', 'validity', 'charges']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    subscription_type = serializers.CharField(
        read_only=True, source="subscription.subscription_type")
    subscription_validity = serializers.IntegerField(
        read_only=True, source="subscription.validity")

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'subscription', 'subscription_type',
                  'subscription_validity', 'valid_from', 'valid_till', 'active']


class AppointmentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointment
        fields = ['id', 'user', 'doctor', 'hospital', 'consultation', 'slot', 'status',
                  'status_update_remark', 'appointment_type', 'original_appointment_ref', 'created_at', 'updated_at']

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'file_path', 'uploaded_by']