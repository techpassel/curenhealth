from rest_framework import serializers
from .models import City, Address, Hospital

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'state', 'added_by']

class AddressSerializer(serializers.ModelSerializer):
    city_detail = CitySerializer(source='city', read_only=True)
    class Meta:
        model = Address
        fields = ['id', 'city', 'city_detail', 'area', 'address', 'landmark',
                  'zipcode', 'country_std_code', 'phone', 'is_default']

class HospitalSerializer(serializers.ModelSerializer):
    address_details = AddressSerializer(source='address', read_only=True)

    class Meta:
        model = Hospital
        fields = ['id', 'hospital_admin', 'hospital_name', 'address', 'address_details', 'details', 'contact_details', 'additional_details']
        extra_kwargs = {
            'hospital_admin': {'validators': []},
            'address': {'validators': []},
            'hospital_name': {'validators': []}
        }