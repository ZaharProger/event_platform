from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

import openpyxl
from openpyxl.styles import Font, Alignment, Color, PatternFill, Border
import os

from django.http import HttpResponse

from tasks.models import Task, UserTask
from .models import DocField, Doc
from users.models import UserPassport


class DocsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        found_doc = Doc.objects.filter(pk=request.GET.get('id', -1))
        data = None

        if len(found_passport) != 0 and len(found_doc) != 0:
            docs_path = os.path.join('event_platform', 'static', found_passport[0].doc_template)
            file = [url for url in os.listdir(docs_path) if found_doc[0].doc_type == url.split('.')[0]]
            if len(file) != 0:
                workbook = openpyxl.load_workbook(os.path.join(docs_path, file[0]))
                doc_sheet = workbook.active

                doc_sheet.cell(row=1, column=2).value = found_doc[0].name
                center_alignment = Alignment(horizontal='center', vertical='center')

                state_colors = {
                    Task.TaskStates.NOT_ASSIGNED: 'eeeeee',
                    Task.TaskStates.ACTIVE: 'ffa726',
                    Task.TaskStates.COMPLETED: '4caf50'
                }

                tasks = Task.objects.filter(event=found_doc[0].event)
                for i in range(len(tasks)):
                    row_number = i + 4

                    task_dates = f'{tasks[i].datetime_start}'
                    if tasks[i].datetime_end is not None:
                        task_dates += f' - {tasks[i].datetime_end}'
                    
                    responsible_user = UserTask.objects.filter(task=tasks[i], is_responsible=True)
                    responsible_user = '' if len(responsible_user) == 0 \
                        else responsible_user[0].user.name
                    
                    task_users = ', '.join([task_user.name for task_user in tasks[i].users.all()])
                    
                    doc_sheet.cell(row=row_number, column=1).value = i + 1
                    doc_sheet.cell(row=row_number, column=2).value = tasks[i].name
                    doc_sheet.cell(row=row_number, column=3).value = task_dates
                    doc_sheet.cell(row=row_number, column=3).alignment = center_alignment
                    doc_sheet.cell(row=row_number, column=4).value = tasks[i].state
                    doc_sheet.cell(row=row_number, column=4).fill = PatternFill(
                        patternType='solid',
                        start_color=Color(state_colors[tasks[i].state])
                    )
                    doc_sheet.cell(row=row_number, column=5).value = responsible_user
                    doc_sheet.cell(row=row_number, column=6).value = task_users

                export_path = os.path.join('event_platform', 'static', 'export', f'{found_doc[0].name}.xlsx')
                workbook.save(export_path)
                workbook.close()
                
            with open(os.path.join(export_path), 'rb') as created_file:
                data = created_file.read()
            os.remove(export_path)

        response = HttpResponse(
            data,
            status=status.HTTP_200_OK if data is not None else status.HTTP_404_NOT_FOUND,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        if data is not None:
            response['Content-Disposition'] = f'attachment; filename="{found_doc[0].name}.xlsx"'

        return response
