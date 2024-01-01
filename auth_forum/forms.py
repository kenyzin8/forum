from django import forms
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input input-bordered w-96 max-w-xs',
        'placeholder': '...',
        'id': 'inpUsername'
    }))

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'input input-bordered w-96 max-w-xs',
        'placeholder': '...',
        'id': 'inpPassword'
    }))