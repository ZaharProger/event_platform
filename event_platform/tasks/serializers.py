from rest_framework.serializers import ModelSerializer

from .models import Task, UserTask
from users.serializers import UserProfileSerializer

class UserTaskSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = UserTask
        fields = ('user', 'is_responsible')


class NestedTaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'name')


class TaskSerializer(ModelSerializer):
    users = UserTaskSerializer(many=True, source='usertask_set')
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'parent', 'name', 'users')
    
    def get_related_field(self, model_field):
        return NestedTaskSerializer()


class TaskNonNestedSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'name')
