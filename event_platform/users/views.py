from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from django.contrib.auth.models import AnonymousUser

from .models import UserProfile, UserPassport
from .forms import UserPassportForm, UserProfileForm
from .serializers import UserPassportSerializer, UserProfileSerializer


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
            else:
                message = 'Введен неверный пароль!'
                response_status = status.HTTP_400_BAD_REQUEST
        else:
            message = 'Пользователя с указанным логином не существует!'
            response_status = status.HTTP_400_BAD_REQUEST
            
        return Response(
            {'message': message}, 
            status=response_status
        )


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response(
            {'message': 'Вы вышли из системы!'}, 
            status=status.HTTP_200_OK
        )


class AccountDataView(APIView):
    def get(self, request):
        # new_user = UserPassport()
        # new_user.username = ''
        # new_user.user = UserProfile.objects.all()[0]
        # new_user.set_password('')
        # new_user.save()
        
        if type(request.user) != AnonymousUser:
            found_passport = UserPassport.objects.filter(username=request.user.username)
            data = UserPassportSerializer(found_passport[0]).data \
                if len(found_passport) != 0 else None
        else:
            data = None

        return Response(
            {'data': data},
            status=status.HTTP_200_OK
        )