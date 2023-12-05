from rest_framework.serializers import ModelSerializer

from .models import DocField, Doc


class DocSerializer(ModelSerializer):
    class Meta:
        model = Doc
        fields = ('id', 'name', 'doc_type')


class DocReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Doc
        fields = ('id',)
