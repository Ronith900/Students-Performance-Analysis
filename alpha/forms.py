from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import *


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CreateTerm(forms.Form):
    term = forms.CharField(label="Term Name", max_length=255)
    subjects = forms.CharField(label="Subjects", max_length=255,
                               widget=forms.TextInput(attrs={'placeholder': 'Comma seperated values eg: Math,Science'}))


class ResultForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'result']
