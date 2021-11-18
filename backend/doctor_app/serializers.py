from django.db import models
from django.db.models import fields
from rest_framework import serializers
from hospital_app.models import Hospital
from hospital_app.serializers import HospitalSerializer
from doctor_app.models import Consultation, ConsultationDefalutTiming, ConsultationSlot, Doctor, Qualification, Speciality


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

class DoctorSerializer(serializers.ModelSerializer):
    qualification_set = DoctorQualificationSerializer(many=True)
    specialities = serializers.PrimaryKeyRelatedField(queryset=Speciality.objects.all(), many=True)
    hospitals = serializers.PrimaryKeyRelatedField(queryset=Hospital.objects.all(), many=True)

    def update(self, instance, validated_data):
        specialities = validated_data.pop('specialities',[])
        hospitals = validated_data.pop('hospitals',[])
        instance.user = validated_data.get('user', instance.user)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.image = validated_data.get('image', instance.image)
        instance.practice_start_year = validated_data.get('practice_start_year', instance.practice_start_year)
        instance.details = validated_data.get('details', instance.details)
        instance.additional_details = validated_data.get('additional_details', instance.additional_details)        
        instance.specialities.set(specialities)
        instance.hospitals.set(hospitals)
        instance.save()
        return instance
    
    def create(self, validated_data):
        qualifications = validated_data.pop('qualification_set')
        specialities = validated_data.pop('specialities')
        hospitals = validated_data.pop('hospitals')
        doctor = Doctor.objects.create(**validated_data)
        for qual in qualifications:
            Qualification.objects.create(doctor=doctor, **qual)
        doctor.specialities.set(specialities)
        doctor.hospitals.set(hospitals)
        doctor.save()
        return doctor

    class Meta:
        model = Doctor
        fields = ["id", "user", "dob", "image", "practice_start_year", "qualification_set",
                  "specialities", "hospitals", "details", "additional_details"]

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ["id", "doctor_user", "consultation_type", "hospital",
                  "location", "address", "charge", "note", "avg_slot_duration"]


class ConsultationDefalutTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationDefalutTiming
        fields = ["id", "consultation", "day_name", "start_hour",
                  "start_minute", "start_period", "end_hour", "end_minute", "end_period"]


class ConsultationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationSlot
        fields = ["id", "consultation", "date", "slot", "availablity"]
