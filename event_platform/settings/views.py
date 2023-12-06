from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from docs.models import Doc, Task
from events.models import Event


class SettingsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        labels_choices = {
            'event_types': Event.EventTypes.choices,
            'doc_types': Doc.DocTypes.choices,
            'task_states': Task.TaskStates.choices
        }
        choices_dict = {}
        for key, value in labels_choices.items():
            choices_dict[key] = [{'label': item[1], 'value': item[0]}  for item in value]

        return Response(
            {'data': choices_dict},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )
