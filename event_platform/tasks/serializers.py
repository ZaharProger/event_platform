from rest_framework.serializers import ModelSerializer

from .models import Task, UserTask
from users.serializers import UserProfileSerializer

class UserTaskSerializer(ModelSerializer):
    user = UserProfileSerializer()
    class Meta:
        model = UserTask
        fields = ('user', 'is_responsible')


class TaskSerializer(ModelSerializer):
    users = UserTaskSerializer(many=True, source='usertask_set')
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'parent', 'name', 'users')
