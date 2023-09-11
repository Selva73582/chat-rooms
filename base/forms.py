from django import forms
from . import models
from django.contrib.auth.forms import UserCreationForm

class Roomform(forms.ModelForm):
    class Meta:
        model=models.Room
        fields="__all__"


