from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event, EventUser
from .forms import EventForm
from users.models import UserPassport
from docs.models import DocField, Doc
from tasks.models import Task, UserTask
from .serializers import EventInfoSerializer, EventCardSerializer, EventNotNestedSerializer

from string import ascii_uppercase, digits
from random import choice
import os


class EventsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_id = request.GET.get('id', None)

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

        return Response(
            {'data': event_serializer.data},
            status=response_status,
            content_type='application/json'
        )

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_form = EventForm(request.POST)

        if event_form.is_valid():
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
                docs = [Doc.objects.create(
                    template_url=url,
                    doc_type=list(filter(
                        lambda choice: choice[0] == url.split('.')[0], 
                        Doc.DocTypes.choices))[0][0]
                ) for url in os.listdir(docs_path)]
                for doc in docs:
                    doc.save()
                    doc.name = f'{doc.doc_type} {doc.pk}'
                    doc.save()
                    added_event.docs.add(doc)

            response_status = status.HTTP_200_OK
        else:
            added_event = None
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {'data': {'id': added_event.id if added_event is not None else None}},
            status=response_status,
            content_type='application/json'
        )

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(pk=request.data['id'])

        if len(found_passport) != 0 and len(found_event) != 0:
            event_serializer = EventNotNestedSerializer(found_event[0], data=request.data)
            if event_serializer.is_valid():
                event_serializer.save()
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        ) 

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_to_delete = request.GET.get('id', None)

        if len(found_passport) != 0 and event_to_delete is not None:
            found_event = Event.objects.filter(pk=event_to_delete)
            if len(found_event) != 0 and found_event[0].users.contains(found_passport[0].user):
                for doc in Doc.objects.filter(event=found_event[0]):
                    for field in DocField.objects.filter(doc=doc):
                        field.delete()
                    doc.delete()
                found_event[0].delete()

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )   

class JoinEventView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(secret_code=request.GET.get('secret_code', '0'))

        if len(found_passport) != 0 and len(found_event) != 0:
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

        if len(found_passport) != 0 and event_to_complete is not None:
            found_event = Event.objects.filter(pk=event_to_complete)
            if len(found_event) != 0 and found_event[0].users.contains(found_passport[0].user):
                found_event[0].is_complete = True
                found_event[0].save()

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )  