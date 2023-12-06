from rest_framework.serializers import ModelSerializer

from .models import Task, UserTask
from users.serializers import UserProfileSerializer

class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'datetime_start', 'datetime_end', 'state', 'parent', 'name')


class UserTaskSerializer(ModelSerializer):
    user = UserProfileSerializer()
    task = TaskSerializer()
    class Meta:
        model = UserTask
        fields = ('task', 'user', 'is_responsible')