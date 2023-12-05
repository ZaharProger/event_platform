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

    def delete(self, request):
        found_passport = UserPassport.objects.filter(username=request.user.username)
        doc_to_delete = request.GET.get('id', None)

        if len(found_passport) != 0 and doc_to_delete is not None:
            found_doc = Doc.objects.filter(pk=doc_to_delete)
            if len(found_doc) != 0 and found_doc[0].event.users.contains(found_passport[0].user):
                for field in DocField.objects.filter(doc=found_doc[0]):
                    field.delete()
                found_doc[0].delete()

        return Response(
            {'message': ''},
            status=status.HTTP_200_OK,
            content_type='application/json'
        )
