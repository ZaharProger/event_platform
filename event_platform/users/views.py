from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import login, logout
from django.db.transaction import atomic
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import UserPassport, UserProfile
from .forms import UserPassportForm
from .serializers import UserPassportSerializer, UserProfileSerializer

from events.models import Event, EventUser

from docs.models import Doc

import os
from string import ascii_letters, digits
from random import choice


class LoginView(APIView):
    def post(self, request):
        user_passport_form = UserPassportForm(request.POST)
        found_passport = UserPassport.objects \
            .filter(username=user_passport_form.data['username'])
        
        if len(found_passport) != 0:
            if found_passport[0].check_password(user_passport_form.data['password']):
                login(request, found_passport[0])
                message = ''
                response_status = status.HTTP_200_OK
                is_superuser = found_passport[0].is_superuser
            else:
                message = 'Введен неверный пароль!'
                response_status = status.HTTP_400_BAD_REQUEST
                is_superuser = False
        else:
            message = 'Пользователя с указанным логином не существует!'
            response_status = status.HTTP_400_BAD_REQUEST
            is_superuser = False
            
        return Response(
            {'message': message, 'is_superuser': is_superuser}, 
            status=response_status,
            content_type='application/json'
        )


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return Response(
            {'message': 'Вы вышли из системы!'}, 
            status=status.HTTP_200_OK,
            content_type='application/json'
        )


class AccountDataView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        data = UserPassportSerializer(found_passport[0]).data \
            if len(found_passport) != 0 else None

        return Response(
            {'data': data},
            status=status.HTTP_200_OK if data is not None else status.HTTP_401_UNAUTHORIZED,
            content_type='application/json'
        )

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)

        if len(found_passport) != 0:
            user_profile_serializer = UserProfileSerializer(found_passport[0].user, data=request.data)
            if user_profile_serializer.is_valid():
                user_profile_serializer.save()
                response_status = status.HTTP_200_OK
            else:
                response_status = status.HTTP_400_BAD_REQUEST

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )
    
    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)

        if len(found_passport) != 0 and found_passport[0].is_superuser:
            with atomic():
                letters_digits = ascii_letters + digits

                new_user_profile = UserProfile.objects.create(
                    name=request.data['name'],
                    email=request.data['email']
                )
                new_user_profile.save()

                new_user = UserPassport()
                new_user.is_superuser = False
                new_user.is_staff = request.data['is_staff']
                new_username = ''.join([choice(ascii_letters) for _ in range(10)])
                new_password = ''.join([choice(letters_digits) for _ in range(10)])

                new_user.username = new_username
                new_user.user = new_user_profile
                new_user.doc_template = request.data['group_name']
                new_user.set_password(new_password)
                new_user.save()

                subject = 'Регистрация на EventPlatform'
                message = ' '.join([
                    f"Здравствуйте, {request.data['name']}!",
                    'Вы были зарегистрированы на EventPlatform!',
                    f'Ваши данные для входа: логин - {new_username}, пароль - {new_password}',
                ])
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [request.data['email']]
                send_mail(subject, message, from_email, recipient_list)
            
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        user_to_delete = request.GET.get('id', None)

        if len(found_passport) != 0 and user_to_delete is not None and found_passport[0].is_superuser:
            for user in UserProfile.objects.filter(pk=user_to_delete):
                user.delete()
            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )
    

class UserGroupsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        group_name = request.GET.get('name', None)
        templates_path = os.path.join('event_platform', 'static')

        if len(found_passport) != 0 and found_passport[0].is_superuser:
            if group_name is None:
                odd_dir_list = ['export', '.DS_Store']
                data = [{'name': dir} for dir in os.listdir(templates_path) if \
                        dir not in odd_dir_list]
                response_status = status.HTTP_200_OK if len(data) != 0 \
                    else status.HTTP_404_NOT_FOUND
            else:
                group_users = UserPassport.objects.filter(doc_template=group_name)
                serialized_group_users = UserPassportSerializer(group_users, many=True).data
                group_docs = []
                group_path = os.path.join(templates_path, group_name)
                with open(os.path.join(group_path, 'config.txt'), 'r') as config:
                    config_lines = config.readlines()
                    doc_index = -1

                    for line in config_lines:
                        if ':' in line:
                            group_docs.append({
                                'name': line.strip().split(':')[0], 
                                'fields': [],
                                'doc_template': None
                            })
                            doc_index += 1
                        else:
                            splitted_line = line.strip().split('|')
                            group_docs[doc_index]['fields'].append({
                                'name': splitted_line[0],
                                'type': splitted_line[1]
                            })
            
                group_doc_files = os.listdir(group_path)
                for i in range(len(group_doc_files)):
                    found_index = [j for j in range(len(group_docs)) \
                                   if group_docs[j]['name'] in group_doc_files[i]]
                    if len(found_index) != 0:
                        group_docs[found_index[0]]['doc_template'] = os.path.join(
                            group_path,
                            group_doc_files[i]
                        )
            
                data = {
                    'name': group_name, 
                    'users': serialized_group_users, 
                    'docs': group_docs
                }
                response_status = status.HTTP_200_OK
        else:
            data = []
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'data': data},
            status=response_status,
            content_type='application/json'
        ) 

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        if len(found_passport) != 0 and found_passport[0].is_superuser:
            docs_path = os.path.join('event_platform', 'static', request.data['name'])
            os.mkdir(docs_path)
            with open(os.path.join(docs_path, 'config.txt'), 'w') as f:
                for i in range(len(Doc.DocTypes.choices)):
                    last = i == len(Doc.DocTypes.choices) - 1
                    f.write(f'{Doc.DocTypes.choices[i][0]}:{'' if last else '\n'}')

            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        ) 

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)

        if len(found_passport) != 0 and found_passport[0].is_superuser:
            UserPassport.objects \
                .filter(doc_template=request.data['old_name']) \
                .update(doc_template=request.data['name'])
                
            group_path = os.path.join('event_platform', 'static')
            old_path = os.path.join(group_path, request.data['old_name'])
            new_path = os.path.join(group_path, request.data['name'])
            os.rename(old_path, new_path)

            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        group_to_delete = request.GET.get('name', None)

        if len(found_passport) != 0 and group_to_delete is not None and found_passport[0].is_superuser:
            passports_to_update = UserPassport.objects.filter(doc_template=group_to_delete)
            for passport in passports_to_update:
                passport.doc_template = ''
                passport.save()

            group_path = os.path.join('event_platform', 'static', group_to_delete)
            for group_file in os.listdir(group_path):
                os.remove(os.path.join(group_path, group_file))
            os.rmdir(group_path)

            response_status = status.HTTP_200_OK
        else:
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'message': ''},
            status=response_status,
            content_type='application/json'
        )


class UsersView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        event_id = request.GET.get('id', None)

        if event_id is not None and len(found_passport) != 0 and found_passport[0].is_staff:
            found_event = Event.objects.filter(pk=event_id)
            if len(found_event) != 0:
                data = UserPassportSerializer(
                    UserPassport.objects.filter(~Q(pk=found_passport[0].pk), is_superuser=False), 
                    many=True
                ).data

                for i in range(len(data)):
                    found_relation = EventUser.objects.filter(
                        event=found_event[0],
                        user=UserProfile.objects.filter(pk=data[i]['user']['id'])[0]
                    )
                    data[i]['is_event_member'] = len(found_relation) != 0
            else:
                data = []

            response_status = status.HTTP_200_OK
        else:
            data = []
            response_status = status.HTTP_403_FORBIDDEN

        return Response(
            {'data': data},
            status=response_status,
            content_type='application/json'
        ) 