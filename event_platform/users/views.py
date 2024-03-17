from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import UserPassport
from .forms import UserPassportForm
from .serializers import UserPassportSerializer, UserProfileSerializer

import os


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
        # user_profile = UserProfile.objects.create(
        #     name='',
        #     email=''
        # )
        # user_profile.save()
        # new_user = UserPassport()
        # new_user.is_superuser = True
        # new_user.username = ''
        # new_user.user = user_profile
        # new_user.set_password('')
        # new_user.save()
        
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
            {'data': ''},
            status=response_status,
            content_type='application/json'
        ) 
    

class UserGroupsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        group_name = request.GET.get('name', None)

        if group_name is None:
            templates_path = os.path.join('event_platform', 'static')
            odd_dir_list = ['export', '.DS_Store']
            data = [{'name': dir} for dir in os.listdir(templates_path) if dir not in odd_dir_list]
            response_status = status.HTTP_200_OK if len(data) != 0 else status.HTTP_404_NOT_FOUND
        else:
            group_users = UserPassport.objects.filter(doc_template=group_name)
            serialized_group_users = UserPassportSerializer(group_users, many=True).data
            data = {'name': group_name, 'users': serialized_group_users, 'docs': []}
            response_status = status.HTTP_200_OK

        return Response(
            {'data': data},
            status=response_status,
            content_type='application/json'
        ) 

    def post(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        if len(found_passport) != 0:
            found_passport[0].doc_template = request.data['name']
            found_passport[0].save()
            docs_path = os.path.join('event_platform', 'static', request.data['name'])
            os.mkdir(docs_path)

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        ) 

    def put(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        if len(found_passport) != 0:
            pass

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        group_to_delete = request.GET.get('name', None)

        if len(found_passport) != 0 and group_to_delete is not None:
            passports_to_update = UserPassport.objects.filter(doc_template=group_to_delete)
            for passport in passports_to_update:
                passport.doc_template = ''
                passport.save()

            os.rmdir(os.path.join('event_platform', 'static', group_to_delete))

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )
    