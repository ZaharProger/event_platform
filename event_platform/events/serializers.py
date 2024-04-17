from rest_framework.serializers import ModelSerializer

from .models import Event, EventUser
from tasks.serializers import TaskSerializer
from docs.serializers import DocSerializer, DocReadOnlySerializer
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
    docs = DocReadOnlySerializer(many=True)
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'users', 'event_form', 'event_type',
            'event_level', 'event_character', 'is_online', 'for_students', 'docs',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )


class EventNotNestedSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'event_form', 'event_type',
            'event_level', 'event_character', 'is_online', 'for_students',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )


class EventCardSerializer(ModelSerializer):
    users = EventUserSerializer(many=True, source='eventuser_set')
    tasks = TaskSerializer(many=True)
    docs = DocSerializer(many=True)
    class Meta:
        model = Event
        fields = (
            'id', 'name', 'place', 'users', 'event_form', 'event_type',
            'event_level', 'event_character', 'is_online', 'for_students', 'docs', 'tasks',
            'datetime_start', 'datetime_end', 'is_complete', 'description'
        )
