from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from docs.models import Doc, DocField
from tasks.models import Task
from events.models import Event


class SettingsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        labels_choices = {
            'event_types': Event.EventTypes.choices,
            'event_levels': Event.EventLevels.choices,
            'event_characters': Event.EventCharacters.choices,
            'doc_types': Doc.DocTypes.choices,
            'task_states': Task.TaskStates.choices
        }
        if request.user.is_superuser:
            labels_choices['field_types'] = DocField.FieldTypes.choices

        choices_dict = {}
        for key, value in labels_choices.items():
            choices_dict[key] = [{'label': item[1], 'value': item[0]}  for item in value]

        return Response(
            {'data': choices_dict},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )
