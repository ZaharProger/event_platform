from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event, EventUser
from .forms import EventForm
from users.models import UserPassport, UserProfile
from docs.models import DocField, Doc, FieldValue
from .serializers import EventInfoSerializer, EventCardSerializer, EventNotNestedSerializer
from tasks.models import UserTask, Task

from string import ascii_uppercase, digits
from random import choice
import os


class EventsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_id = request.GET.get('id', None)

        if len(found_passport) != 0 and not found_passport[0].is_superuser:
            if event_id is not None:
                events = Event.objects.filter(pk=event_id)
                event_serializer = EventCardSerializer(
                    [event for event in events if event.users.contains(found_passport[0].user)],
                    many=True
                )
                response_status = status.HTTP_200_OK if len(event_serializer.data) != 0 \
                    else status.HTTP_404_NOT_FOUND
            else:
                events = Event.objects.all().order_by('-pk')
                event_serializer = EventInfoSerializer(
                    [event for event in events if event.users.contains(found_passport[0].user)], 
                    many=True
                )
                response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'data': event_serializer.data},
            status=response_status,
            content_type='application/json'
        )

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_form = EventForm(request.POST)

        if event_form.is_valid() and len(found_passport) != 0 and found_passport[0].is_staff:
            secret_code_symbols = ascii_uppercase + digits

            with atomic():
                added_event = event_form.save()
                added_event.secret_code = ''.join([choice(secret_code_symbols) for _ in range(8)])
                added_event.save()

                event_user = EventUser.objects.create(
                    event=added_event,
                    user=found_passport[0].user if len(found_passport) != 0 else None,
                    is_organizer=True
                )
                event_user.save()

                docs_path = os.path.join('event_platform', 'static', found_passport[0].doc_template)
                docs = []
                with open (os.path.join(docs_path, 'config.txt'), 'r') as config:
                    config_lines = [line.split(':')[0] for line in config.readlines() \
                                    if ':' in line]

                for line in config_lines:
                    recognized_doc_type = list(filter(
                        lambda choice: choice[0] == line and choice[0] != Doc.DocTypes.REPORT, 
                        Doc.DocTypes.choices)
                    )
                    if len(recognized_doc_type) != 0:
                        doc_type_value = recognized_doc_type[0][0]
                        url = [filename for filename in os.listdir(docs_path) \
                               if line in filename]
                        doc_template_url = os.path.join(
                            found_passport[0].doc_template, 
                            url[0] if len(url) != 0 else doc_type_value
                        )
                        new_doc = Doc.objects.create(
                            template_url=doc_template_url,
                            doc_type=doc_type_value,
                            name=doc_type_value
                        )
                        docs.append(new_doc)
                
                with open(os.path.join(docs_path, 'config.txt')) as config:
                    config_data = config.readlines()
                    config_dict = {}
                    last_key = ''

                    for line in config_data:
                        splitted_line = line.split(':')
                        if len(splitted_line) != 0 and splitted_line[0] in Doc.DocTypes.values:
                            config_dict[splitted_line[0]] = []
                            last_key = splitted_line[0]
                        else:
                            config_dict[last_key].append(line.strip())
                    
                for doc in docs:
                    doc.save()
                    if doc.doc_type in config_dict.keys():
                        for field in config_dict[doc.doc_type]:
                            splitted_field = field.split('|')
                            new_field = DocField.objects.create(
                                doc=doc,
                                name=splitted_field[0],
                                field_type=splitted_field[1]
                            )
                            new_field.save()
                            new_value = FieldValue.objects.create(
                                field=new_field,
                                value=''
                            )
                            new_value.save()

                    added_event.docs.add(doc)

                added_event.save()

            response_status = status.HTTP_200_OK
        else:
            added_event = None
            if len(found_passport) != 0 and found_passport[0].is_staff:
                response_status = status.HTTP_400_BAD_REQUEST
            else:
                response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'data': {'id': added_event.id if added_event is not None else None}},
            status=response_status,
            content_type='application/json'
        )

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(pk=request.data['id'])

        if len(found_passport) != 0 and len(found_event) != 0 and found_passport[0].is_staff:
            event_serializer = EventNotNestedSerializer(found_event[0], data=request.data)
            if event_serializer.is_valid():
                event_serializer.save()
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_400_BAD_REQUEST
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        ) 

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_to_delete = request.GET.get('id', None)

        if len(found_passport) != 0 and event_to_delete is not None and found_passport[0].is_staff:
            found_event = Event.objects.filter(pk=event_to_delete)
            if len(found_event) != 0 and found_event[0].users.contains(found_passport[0].user):
                found_relation = EventUser.objects.filter(
                    event=found_event[0], 
                    user=found_passport[0].user
                )
                if found_relation[0].is_organizer:
                    for doc in Doc.objects.filter(event=found_event[0]):
                        for field in DocField.objects.filter(doc=doc):
                            field.delete()
                        doc.delete()
                    found_event[0].delete()
                
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_403_FORBIDDEN
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )   


class JoinEventView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(secret_code=request.GET.get('secret_code', '0'))

        if len(found_passport) != 0 and len(found_event) != 0 and not found_passport[0].is_superuser:
            if not found_event[0].users.contains(found_passport[0].user):
                found_event[0].users.add(found_passport[0].user)
                response_status = status.HTTP_200_OK
                message = ''
            else:
                response_status = status.HTTP_400_BAD_REQUEST
                message = 'Вы уже присоединились к данному мероприятию!'
        else:
            response_status = status.HTTP_404_NOT_FOUND
            message = 'Не найдено мероприятия по введенному коду приглашения!'
        
        return Response(
            {'message': message},
            status=response_status,
            content_type='application/json'
        )


class CompleteEventView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_to_complete = request.GET.get('id', None)

        if len(found_passport) != 0 and event_to_complete is not None and found_passport[0].is_staff:
            found_event = Event.objects.filter(pk=event_to_complete)
            if len(found_event) != 0 and found_event[0].users.contains(found_passport[0].user):
                found_relation = EventUser.objects.filter(
                    event=found_event[0], 
                    user=found_passport[0].user
                )
                if found_relation[0].is_organizer:
                    found_event[0].is_complete = True
                    found_event[0].save()
                
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_403_FORBIDDEN
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        ) 


class InviteEventUsersView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(pk=request.data['event_id'])

        if len(found_passport) != 0 and found_passport[0].is_staff and len(found_event) != 0:
            request_user_ids = [request_user['id'] for request_user in request.data['users']]
            event_organizer = EventUser.objects.filter(event=found_event[0], is_organizer=True)[0]

            for event_user in EventUser.objects.filter(event=found_event[0], is_organizer=False):
                if event_user.user.pk not in request_user_ids:
                    event_user.delete()
            
            for task_user in UserTask.objects.all():
                if task_user.user.pk not in request_user_ids and \
                    event_organizer.user.pk != task_user.user.pk:
                    task_user.delete()

            subject = 'EventPlatform: приглашение в организационный комитет'
            from_email = settings.EMAIL_HOST_USER
            for event_user in request.data['users']:
                found_user = UserProfile.objects.filter(pk=event_user['id'])

                if len(found_user) != 0 and found_user[0] not in found_event[0].users.all():
                    message = ' '.join([
                        f"Здравствуйте, {found_user[0].name}!",
                        f"Вы были приглашены на мероприятие \"{found_event[0].name}\" в EventPlatform!",
                        f"Код доступа к мероприятию: {found_event[0].secret_code}. Присоединяйтесь!",
                    ])
                    recipient_list = [found_user[0].email]
                    send_mail(subject, message, from_email, recipient_list)
                    
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )


class CopyEventView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_to_copy = request.GET.get('id', None)

        if len(found_passport) != 0 and event_to_copy is not None and found_passport[0].is_staff:
            found_event = Event.objects.filter(pk=event_to_copy)
            if len(found_event) != 0:
                secret_code_symbols = ascii_uppercase + digits
                with atomic():
                    new_event = Event.objects.create(
                        name=found_event[0].name,
                        event_type=found_event[0].event_type,
                        event_level=found_event[0].event_level,
                        event_character=found_event[0].event_character,
                        event_form=found_event[0].event_form,
                        is_online=found_event[0].is_online,
                        for_students=found_event[0].for_students,
                        is_complete=False,
                        place=found_event[0].place,
                        datetime_start=found_event[0].datetime_start,
                        datetime_end=found_event[0].datetime_end,
                        description=found_event[0].description,
                        secret_code=''.join([choice(secret_code_symbols) for _ in range(8)])
                    )
                    new_event.save()
                    for event_user in EventUser.objects.filter(event=found_event[0]):
                        new_event_user = EventUser.objects.create(
                            event=new_event,
                            user=event_user.user,
                            is_organizer=event_user.is_organizer
                        )
                        new_event_user.save()
                    for doc in Doc.objects.filter(event=found_event[0]):
                        new_doc = Doc.objects.create(
                            doc_type=doc.doc_type,
                            name=doc.name,
                            template_url=doc.template_url,
                            event=new_event
                        )
                        new_doc.save()
                        for field in DocField.objects.filter(doc=doc):
                            new_field = DocField.objects.create(
                                doc=new_doc,
                                name=field.name,
                                field_type=field.field_type
                            )
                            new_field.save()
                            for value in field.values.all():
                                new_value = FieldValue.objects.create(
                                    field=new_field,
                                    value=value.value
                                )   
                                new_value.save()
                    for task in Task.objects.filter(event=found_event[0]):
                        new_task = Task.objects.create(
                            event=new_event,
                            parent=task.parent,
                            datetime_start=task.datetime_start,
                            datetime_end=task.datetime_end,
                            state=task.state,
                            name=task.name
                        )
                        new_task.save()
                        for user_task in UserTask.objects.filter(task=task):
                            new_user_task = UserTask.objects.create(
                                task=new_task,
                                user=user_task.user,
                                is_responsible=user_task.is_responsible
                            )
                            new_user_task.save()

            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )
