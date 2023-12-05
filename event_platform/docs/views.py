from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

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
