from django import forms

from .models import UserProfile, UserPassport


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('email', 'phone', 'telegram', 'organization', 'name')


class UserPassportForm(forms.ModelForm):
    class Meta:
        model = UserPassport
        fields = ('username', 'password')
