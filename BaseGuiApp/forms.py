from django import forms
from django.contrib.auth.models import User



class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)