from rest_framework.serializers import ModelSerializer

from .models import Event
from users.serializers import UserProfileSerializer


class EventShortCardSerializer(ModelSerializer):
    organizer = UserProfileSerializer()

    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'organizer', 'secret_code',
            'datetime_start', 'datetime_end', 'is_complete'
        )
