from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

import os

from django.http import HttpResponse
from django.db.transaction import atomic

from .models import Doc, FieldValue
from .forms import FieldValueForm
from .services import TableDocBuilder, RoadmapSchema, MoneySchema, BuilderShema
from .serializers import FieldValueSerializer
from events.models import Event
from users.models import UserPassport


class DocsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    doc_builders = {
        Doc.DocTypes.ROADMAP: TableDocBuilder(RoadmapSchema()),
        Doc.DocTypes.MONEY: TableDocBuilder(MoneySchema()),
        Doc.DocTypes.PROGRAMME: TableDocBuilder(BuilderShema())
    }

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_event = Event.objects.filter(pk=request.data['event_id'])
        found_doc = Doc.objects.filter(pk=request.data['doc_id'])

        if len(found_passport) != 0 and len(found_event) != 0 and len(found_doc) != 0 and found_passport[0].is_staff:
            with atomic():
                found_doc[0].name = request.data['name']
                found_doc[0].save()

                request_pairs = []
                for field in request.data['fields']:
                    request_pairs.extend([(field['id'], value) for \
                                            value in field['values']])
                request_values = [pair[1]['id'] for pair in request_pairs \
                                  if type(pair[1]['id']) != str]
                for field in found_doc[0].fields.all():
                    for value in field.values.all():
                        if value.pk not in request_values:
                            value.delete()
                
                for pair in request_pairs:
                    found_value = [] if type(pair[1]['id']) == str \
                        else FieldValue.objects.filter(pk=pair[1]['id'])
                    
                    if len(found_value) != 0:
                        value_data = FieldValueSerializer(found_value[0], data=pair[1])
                    else:
                        value_data = FieldValueForm(pair[1])
                    
                    if value_data.is_valid():
                        added_value = value_data.save()
                        if len(found_value) == 0:
                            found_field = [field for field in found_doc[0].fields.all() \
                                           if field.pk == pair[0]]
                            if len(found_field) != 0:
                                added_value.field = found_field[0]
                                added_value.save()
            
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_doc = Doc.objects.filter(pk=request.GET.get('id', -1))
        data = None

        if len(found_passport) != 0 and len(found_doc) != 0 and not found_passport[0].is_superuser:
            docs_path = os.path.join(
                'event_platform', 
                'static', 
                found_passport[0].doc_template
            )
            file = [url for url in os.listdir(docs_path) 
                    if found_doc[0].doc_type == url.split('.')[0]]
            
            if len(file) != 0:
                export_path = os.path.join(
                    'event_platform', 
                    'static', 
                    'export', 
                    f'{found_doc[0].name}.xlsx'
                )
                file_name = file[0]

                DocsView.doc_builders[found_doc[0].doc_type].build(
                    found_doc[0],
                    docs_path,
                    export_path,
                    file_name
                )

                with open(os.path.join(export_path), 'rb') as created_file:
                    data = created_file.read()
                os.remove(export_path)
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_404_NOT_FOUND
        else:
            response_status = status.HTTP_403_FORBIDDEN

        response = HttpResponse(
            data,
            status=response_status,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        if data is not None:
            response['Content-Disposition'] = f'attachment; filename="{found_doc[0].name}.xlsx"'

        return response


class TemplatesView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        data = {}

        if len(found_passport) != 0 and found_passport[0].is_superuser:
            if request.data['upload']:
                template_file = request.FILES['doc_template']
                docs_path = os.path.join('event_platform', 'static', request.data['name'])
                with open(os.path.join(docs_path, template_file.name), 'wb') as f:
                    for chunk in template_file.chunks():
                        f.write(chunk)

                response = HttpResponse(
                    data,
                    status=status.HTTP_200_OK,
                    content_type='application/json'
                )
            else:
                filename = ''
                with open(request.data['doc_template'], 'rb') as template_file:
                    data = template_file.read()
                    filename = os.path.basename(template_file.name)

                _, file_extension = os.path.splitext(request.data['doc_template'])
                if file_extension == '.docx' or file_extension == '.doc':
                    content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                else:
                    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

                response = HttpResponse(
                    data,
                    status=status.HTTP_200_OK,
                    content_type=content_type
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}{file_extension}"'
        else:
            response = HttpResponse(
                data,
                status=status.HTTP_404_NOT_FOUND,
                content_type='application/json'
            )
        
        return response


    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)

        if len(found_passport) != 0 and found_passport[0].is_superuser:
            docs_path = os.path.join('event_platform', 'static', request.data['group_name'])
            config_lines = []

            with open(os.path.join(docs_path, 'config.txt'), 'r') as config:
                config_lines = config.readlines()
            
            found_doc_line = [i for i in range(len(config_lines)) \
                              if ':' in config_lines[i] \
                                and request.data['doc_name'] in config_lines[i]]
            for i in range(found_doc_line[0] + 1, len(config_lines)):
                if ':' in config_lines[i]:
                    break
                else:
                    config_lines[i] = ''
            config_lines = [line for line in config_lines if line != '']

            for i in range(len(request.data['fields'][0]['values'])):
                value_pair = {
                    'name': request.data['fields'][0]['values'][i]['value'], 
                    'type': request.data['fields'][1]['values'][i]['value']
                }
                new_line = f'{value_pair['name']}|{value_pair['type']}\n'

                if found_doc_line[0] == len(config_lines) - 1:
                    config_lines.append(new_line)
                else:
                    config_lines.insert(
                        found_doc_line[0] + i + 1, 
                        new_line
                    )
            
            with open(os.path.join(docs_path, 'config.txt'), 'w') as config:
                config.write(''.join(config_lines))
            
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN
        
        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )