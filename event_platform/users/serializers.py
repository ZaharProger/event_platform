from rest_framework.serializers import ModelSerializer

from .models import UserProfile, UserPassport


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'email', 'phone', 'telegram', 'organization', 'name')


class UserProfileReadOnlySerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', )


class UserPassportSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = UserPassport
        fields = ('username', 'user', 'is_superuser', 'is_staff')
