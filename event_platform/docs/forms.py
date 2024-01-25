from django import forms

from .models import FieldValue


class FieldValueForm(forms.ModelForm):
    class Meta:
        model = FieldValue
        fields = ('value',)
