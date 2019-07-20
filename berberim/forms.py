from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserType
from django.utils.translation import gettext as _


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    user_type = forms.ModelChoiceField(
        queryset=UserType.objects.all().exclude(name='admin'),
        widget=forms.Select(
            attrs={'class': 'd-none'}
        ),
        initial=UserType.objects.get(name='customer')
    )

    class Meta:
	    model = User
	    fields = ["email", "password1", "password2", "user_type"]


class UserForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    class Meta:
        model = User
        fields = ['email', 'password']