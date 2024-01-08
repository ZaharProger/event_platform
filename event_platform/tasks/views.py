from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.models import UserProfile, UserPassport
from users.serializers import UserProfileSerializer
from .models import Task, UserTask
from events.models import Event
from .serializers import TaskNonNestedSerializer, UserTaskSerializer
from .forms import TaskForm
from docs.models import Doc


class TasksView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(pk=request.data['event_id'])
        found_doc = Doc.objects.filter(pk=request.data['doc_id'])

        if len(found_passport) != 0 and len(found_event) != 0 and len(found_doc) != 0:
            with atomic():
                found_doc[0].name = request.data['name']
                found_doc[0].save()

                request_tasks = [task['id'] for task in request.data['tasks']]
                for task in Task.objects.filter(event=found_event[0].id):
                    if task.pk not in request_tasks:
                        task.delete()
                
                created_tasks_ids = {task['id']: -1 for task in request.data['tasks'] \
                                    if type(task['id']) == str}

                sorted_tasks = sorted(
                    request.data['tasks'], 
                    key=lambda item: -1 if item['parent'] is None else 1
                )
                for task in sorted_tasks:
                    found_task = [] if type(task['id']) == str \
                        else Task.objects.filter(pk=task['id'])
                    
                    if len(found_task) != 0:
                        task_data = TaskNonNestedSerializer(found_task[0], data=task)
                    else:
                        task_data = TaskForm(task)
                    
                    if task_data.is_valid():
                        added_task = task_data.save()                       

                        if len(found_task) != 0:
                            parent_task_id = found_task[0].parent.id \
                                if found_task[0].parent is not None else -1
                        else:
                            created_tasks_ids[task['id']] = added_task.pk
                            if task['parent'] in created_tasks_ids.keys():
                                parent_task_id = created_tasks_ids[task['parent']] \
                                    if task['parent'] is not None else -1 
                            else:
                                parent_task_id = task['parent'] \
                                    if task['parent'] is not None else - 1                      
                    
                        parent_task = None
                        for db_task in Task.objects.filter(event=found_event[0].id):
                            if db_task.id == parent_task_id:
                                parent_task = db_task
                                break
                        
                        added_task.parent = parent_task

                        for user in task['users']:                         
                            found_user = UserProfile.objects.filter(pk=user['user']['id'])
                            if len(found_user) != 0:
                                found_relation = UserTask.objects.filter(
                                    task=added_task,
                                    user=found_user[0]
                                )
                                if len(found_relation) == 0:
                                    user_task = UserTask.objects.create(
                                        user=found_user[0],
                                        task=added_task,
                                        is_responsible=user['is_responsible']
                                    )
                                    user_task.save()
                                else:
                                    found_relation[0].is_responsible = user['is_responsible']
                                    found_relation[0].save()

                        task_users = [user['user']['id'] for user in task['users']]
                        for user_task in UserTask.objects.filter(task=added_task):
                            if user_task.user.id not in task_users:
                                user_task.delete()

                        added_task.event = found_event[0]
                        added_task.save()

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        ) 