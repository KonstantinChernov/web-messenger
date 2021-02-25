from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control',
                                                                       'placeholder': 'username'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                            'placeholder': 'password'}))


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control',
                                                                       'placeholder': 'username'}))
    email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control',
                                                                      'placeholder': 'email'}))
    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                            'placeholder': 'password'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                            'placeholder': 'password again'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

