from rest_framework.serializers import ModelSerializer

from .models import Event, EventUser
from users.serializers import UserProfileSerializer


class EventUserSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = EventUser
        fields = ('is_organizer', 'user')


class EventShortCardSerializer(ModelSerializer):
    users = EventUserSerializer(many=True, source='eventuser_set')
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'secret_code', 'users',
            'datetime_start', 'datetime_end', 'is_complete'
        )
