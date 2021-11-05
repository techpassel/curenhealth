from django.contrib.postgres import fields
from rest_framework import serializers
from enumchoicefield import EnumChoiceField
from .models import City, Address


# class UserSerializer(serializers.ModelSerializer):
class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state', 'added_by']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'city', 'area', 'address', 'landmark',
                  'zipcode', 'country_code', 'phone', 'is_default']
