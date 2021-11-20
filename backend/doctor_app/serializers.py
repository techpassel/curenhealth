from enumchoicefield.fields import EnumChoiceField
from rest_framework import serializers
from hospital_app.serializers import AddressSerializer, HospitalSerializer, HospitalBriefSerializer
from doctor_app.models import ClientStaff, ClientStaffPermissions, ClientStaffSecondaryRoles, Consultation, ConsultationDefalutTiming, ConsultationSlot, Doctor, Qualification, Speciality
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
        fields = ["id", "doctor", "degree",
                  "institute", "passing_year", "remark"]


class DoctorQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ["id", "degree", "institute", "passing_year", "remark"]


class ConsultationDefalutTimingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationDefalutTiming
        fields = ["id", "consultation", "day_name", "start_hour",
                  "start_minute", "start_period", "end_hour", "end_minute", "end_period"]


class ConsultationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationSlot
        fields = ["id", "consultation_timing", "date", "slot", "availablity"]


class ConsultationSerializer(serializers.ModelSerializer):
    address_details = AddressSerializer(source="address", read_only=True)
    consultation_timing = ConsultationDefalutTimingSerializer(
        source="timing_related_consultation", read_only=True, many=True)

    class Meta:
        model = Consultation
        fields = ["id", "doctor", "consultation_type", "consultation_timing", "hospital",
                  "location", "address", "address_details", "consultation_fee", "note", "avg_slot_duration"]


class DoctorNameSerializer(serializers.ModelSerializer):
    # doctor_name = UserSerializer(source="user.get_full_name", read_only=True)
    doctor_name = serializers.SerializerMethodField('get_doctor_name')

    def get_doctor_name(self, obj):
        return obj.user.get_full_name()
    class Meta:
        model = Doctor
        fields = ["id", "doctor_name"]


class DoctorsBriefSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)
    hospitals_details = HospitalBriefSerializer(
        source="hospitals", many=True, read_only=True)
    specialities_details = SpecialityBriefSerializer(
        source="specialities", many=True, read_only=True)
    consultations = ConsultationSerializer(many=True)

    class Meta:
        model = Doctor
        fields = ["id", "user", "user_details", "dob", "image", "practice_start_year",
                  "hospitals_details", "specialities_details", "details", "additional_details", "consultations"]


class DoctorSerializer(serializers.ModelSerializer):
    qualification_set = DoctorQualificationSerializer(many=True)
    specialities_details = SpecialitySerializer(
        source="specialities", many=True, read_only=True)
    hospitals_details = HospitalSerializer(
        source="hospitals", many=True, read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    consultations = ConsultationSerializer(
        source="consultation_doctor", many=True, read_only=True)

    def update(self, instance, validated_data):
        specialities = validated_data.pop('specialities', None)
        hospitals = validated_data.pop('hospitals', None)
        instance.user = validated_data.get('user', instance.user)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.image = validated_data.get('image', instance.image)
        instance.practice_start_year = validated_data.get(
            'practice_start_year', instance.practice_start_year)
        instance.details = validated_data.get('details', instance.details)
        instance.additional_details = validated_data.get(
            'additional_details', instance.additional_details)
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


class ClientStaffSerializer(serializers.ModelSerializer):
    doctor_details = DoctorNameSerializer(source="doctor", read_only=True)
    class Meta:
        model = ClientStaff
        fields = ["id", "user", "doctor", "doctor_details", "hospital", "pathlab", "permissions"]


class ClientStaffSecondaryRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientStaffSecondaryRoles
        fields = ["id", "staff", "secondary_role",
              "doctor", "hospital", "pathlab", "permissions"]
