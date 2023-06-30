# judgeapp/forms.py

from django import forms
from django.forms import ModelForm
from .models import Submission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()
class CreateUserForm(UserCreationForm):
    
    email = forms.EmailField(label='Email',widget=forms.TextInput(attrs={"placeholder":"Email","id":"email"})) 
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']


class CodeForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['user_code']
        widgets = {'user_code' : forms.Textarea()} 