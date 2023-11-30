from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Event
from .forms import EventForm
from users.models import UserPassport
from .serializers import EventShortCardSerializer


class EventsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        events = Event.objects.filter(organizer=found_passport[0].user) \
            if len(found_passport) != 0 else []
        
        event_serializer = EventShortCardSerializer(events, many=True)

        return Response(
            {'data': event_serializer.data},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            with atomic:
                added_event = event_form.save()
                added_event.organizer = found_passport[0].user if len(found_passport) != 0 else None
                added_event.save()
            response_status = status.HTTP_200_OK
        else:
            print(event_form.errors)
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )
