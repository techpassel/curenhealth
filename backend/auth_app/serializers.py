from rest_framework import serializers
from enumchoicefield import EnumChoiceField
from .models import User, UserType

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')
        # If want only few fields isntead of all then define it as follows:
        # fields = ['email', 'username', 'password', 'token']

    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(max_length=80)
    country_code = serializers.CharField(max_length=11, required=False)
    contact_num = serializers.IntegerField()
    password = serializers.CharField(max_length=256)
    usertype = EnumChoiceField(UserType)

