from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from django.contrib.auth import authenticate, login, logout
from rest_framework import status

from .models import UserProfile, UserPassport
from .forms import UserPassportForm, UserProfileForm


class LoginView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request):
        user_passport_form = UserPassportForm(request.POST, instance=request.user)
        if user_passport_form.is_valid():
            user = authenticate(
                request, 
                username=user_passport_form.username, 
                password=user_passport_form.password
            )
            if user is not None:
                login(request, user)
                response = Response(
                    {'message': 'Успешный вход!'}, 
                    status=status.HTTP_200_OK
                )
            else:
                response = Response(
                    {'message': 'Неверный логин или пароль!'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            response = Response(
                {'message': ''}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return response


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response(
            {'message': 'Вы вышли из системы!'}, 
            status=status.HTTP_200_OK
        )