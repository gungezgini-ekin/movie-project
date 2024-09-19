from django.contrib.auth.models import User
from django.forms import ModelForm

from users.models import Profile, ListName
from django import forms


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'image']


class NewListForm(ModelForm):
    class Meta:
        model = ListName
        fields = ['name', 'is_private']
        labels = {
            'is_private': "Do you want this list to be private?"
        }
