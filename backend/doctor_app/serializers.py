from django.db import models
from django.db.models import fields
from rest_framework import serializers
from hospital_app.models import Hospital
from hospital_app.serializers import AddressSerializer, HospitalSerializer, HospitalBriefSerializer
from doctor_app.models import Consultation, ConsultationDefalutTiming, ConsultationSlot, Doctor, Qualification, Speciality
from user_app.serializers import UserSerializer

class SpecialityBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ["id", "name"]

class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ["id", "name", "description", "related_speciality"]

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "doctor", "degree", "institute", "passing_year", "remark"]

class DoctorQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "degree", "institute", "passing_year", "remark"]


class ConsultationSerializer(serializers.ModelSerializer):
    address_details = AddressSerializer(source="address", read_only=True)
    class Meta:
        model = Consultation
        fields = ["id", "doctor", "consultation_type", "hospital",
                  "location", "address", "address_details", "consultation_fee", "note", "avg_slot_duration"]


class DoctorsBriefSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    hospitals_details = HospitalBriefSerializer(source="hospitals", many=True, read_only=True)
    specialities_details = SpecialityBriefSerializer(source="specialities", many=True, read_only=True)
    consultations = ConsultationSerializer(many=True)
    class Meta:
        model = Doctor
        fields = ["id", "user", "user_details", "dob", "image", "practice_start_year", "hospitals_details", "specialities_details", "details", "additional_details", "consultations"]    


class DoctorSerializer(serializers.ModelSerializer):
    qualification_set = DoctorQualificationSerializer(many=True)
    specialities_details = SpecialitySerializer(source="specialities", many=True, read_only=True)
    hospitals_details = HospitalSerializer(source="hospitals", many=True, read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    consultations = ConsultationSerializer(source="consultation_doctor", many=True)

    def update(self, instance, validated_data):
        specialities = validated_data.pop('specialities', None)
        hospitals = validated_data.pop('hospitals', None)
        instance.user = validated_data.get('user', instance.user)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.image = validated_data.get('image', instance.image)
        instance.practice_start_year = validated_data.get('practice_start_year', instance.practice_start_year)
        instance.details = validated_data.get('details', instance.details)
        instance.additional_details = validated_data.get('additional_details', instance.additional_details)        
        if specialities != None:
            instance.specialities.set(specialities)
        if hospitals != None:
            instance.hospitals.set(hospitals)
        instance.save()
        return instance
    
    def create(self, validated_data):
        qualifications = validated_data.pop('qualification_set')
        specialities = validated_data.pop('specialities', [])
        hospitals = validated_data.pop('hospitals', [])
        doctor = Doctor.objects.create(**validated_data)
        for qual in qualifications:
            Qualification.objects.create(doctor=doctor, **qual)
        doctor.specialities.set(specialities)
        doctor.hospitals.set(hospitals)
        doctor.save()
        return doctor

    class Meta:
        model = Doctor
        fields = ["id", "user", "user_details", "dob", "image", "practice_start_year", "qualification_set",
                  "specialities", "specialities_details", "hospitals", "hospitals_details", "consultations", "details", "additional_details"]


class ConsultationDefalutTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationDefalutTiming
        fields = ["id", "consultation", "day_name", "start_hour",
                  "start_minute", "start_period", "end_hour", "end_minute", "end_period"]


class ConsultationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationSlot
        fields = ["id", "consultation", "date", "slot", "availablity"]