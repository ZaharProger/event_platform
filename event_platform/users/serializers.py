from rest_framework.serializers import ModelSerializer

from .models import UserProfile, UserPassport


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('email', 'phone', 'telegram', 'organization', 'name', 'surname', 'middle_name')


class UserPassportSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = UserPassport
        fields = ('username', 'user', 'is_superuser', 'is_staff')
