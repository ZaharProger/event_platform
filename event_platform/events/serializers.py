from rest_framework.serializers import ModelSerializer

from .models import Event, EventUser
from users.serializers import UserProfileReadOnlySerializer, UserProfileSerializer


class EventUserReadOnlySerializer(ModelSerializer):
    user = UserProfileReadOnlySerializer()
    class Meta:
        model = EventUser
        fields = ('is_organizer', 'user')


class EventUserSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = EventUser
        fields = ('is_organizer', 'user')


class EventInfoSerializer(ModelSerializer):
    users = EventUserReadOnlySerializer(many=True, source='eventuser_set')
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'users', 'event_type', 'is_online',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )


class EventNotNestedSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'event_type', 'is_online',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )


class EventCardSerializer(ModelSerializer):
    users = EventUserSerializer(many=True, source='eventuser_set')
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'users', 'event_type', 'is_online',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )