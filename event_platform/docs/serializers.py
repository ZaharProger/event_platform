from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import DocField, Doc, FieldValue


class FieldValueSerializer(ModelSerializer):
    class Meta:
        model = FieldValue
        fields = ('id', 'value',)


class DocFieldSerializer(ModelSerializer):
    values = FieldValueSerializer(many=True)
    class Meta:
        model = DocField
        fields = ('id', 'name', 'values')


class DocSerializer(ModelSerializer):
    fields = DocFieldSerializer(many=True)
    is_table = SerializerMethodField('get_is_table')

    def get_is_table(self, obj):
        return obj.doc_type in [Doc.DocTypes.ROADMAP, Doc.DocTypes.MONEY, Doc.DocTypes.PROGRAMME]
    
    class Meta:
        model = Doc
        fields = ('id', 'name', 'doc_type', 'fields', 'is_table')


class DocReadOnlySerializer(ModelSerializer):
    class Meta:
        model = Doc
        fields = ('id',)
