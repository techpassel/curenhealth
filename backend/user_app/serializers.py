from django.db.models import fields
from rest_framework import serializers
from enumchoicefield import EnumChoiceField

from auth_app.models import User

from .models import HealthRecord, HealthRecordTypes, SubscriptionScheme, UserDetail


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['id', 'user', 'dob', 'height', 'weight',
                  'blood_group', 'image']

class HealthRecordsSerializer(serializers.ModelSerializer):
    added_by_name = serializers.CharField(read_only=True, source="user.get_full_name") 
    type = EnumChoiceField(HealthRecordTypes)
    class Meta:
        model = HealthRecord
        fields = ['id', 'user', 'type', 'other_type_name', 'value', 'details', 'is_latest', 'added_by', 'added_by_name', 'measured_by', 'report_url', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

class SubscriptionSchemesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionScheme
        fields = ['id', 'subscription_type', 'validity', 'charges']