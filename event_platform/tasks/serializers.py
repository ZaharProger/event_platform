from rest_framework.serializers import ModelSerializer

from .models import Task, UserTask
from users.serializers import UserProfileSerializer

class UserTaskSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = UserTask
        fields = ('user', 'is_responsible')


class NestedTasksSerializer(ModelSerializer):
    users = UserTaskSerializer(many=True, source='usertask_set')
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'name', 'users')


class TaskSerializer(ModelSerializer):
    users = UserTaskSerializer(many=True, source='usertask_set')
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'nested_tasks', 'name', 'users')
    
    def get_related_field(self, model_field):
        return NestedTasksSerializer()


class TaskNonNestedSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'name')
