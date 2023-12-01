from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event, EventUser
from .forms import EventForm
from users.models import UserPassport
from .serializers import EventInfoSerializer

from string import ascii_uppercase, digits
from random import choice


class EventsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        events = [event for event in Event.objects.all() if event.users.contains(found_passport[0].user)]
        
        event_serializer = EventInfoSerializer(events, many=True)

        return Response(
            {'data': event_serializer.data},
            status=status.HTTP_200_OK,
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
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )


class JoinEventView(APIView):
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
