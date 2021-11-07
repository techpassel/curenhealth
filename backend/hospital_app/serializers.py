from django.contrib.postgres import fields
from rest_framework import serializers
from enumchoicefield import EnumChoiceField
from .models import City, Address

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state', 'added_by']


class AddressSerializer(serializers.ModelSerializer):
    city_detail = CitySerializer(source='city', read_only=True)
    class Meta:
        model = Address
        fields = ['id', 'city', 'city_detail', 'area', 'address', 'landmark',
                  'zipcode', 'country_code', 'phone', 'is_default']
