from rest_framework.serializers import ModelSerializer

from .models import Event, EventUser
from users.serializers import UserProfileReadOnlySerializer


class EventUserReadOnlySerializer(ModelSerializer):
    user = UserProfileReadOnlySerializer()
    class Meta:
        model = EventUser
        fields = ('is_organizer', 'user')


class EventInfoSerializer(ModelSerializer):
    users = EventUserReadOnlySerializer(many=True, source='eventuser_set')
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'secret_code', 'users', 'event_type', 'is_online',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )
