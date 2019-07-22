from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserType, Barbershop, BarbershopEmployee, EMPLOYEE_TITLES_CHOICES, SERVICE_NAME_CHOICES, Address, BarbershopServices
from django.utils.translation import gettext as _
import re


class RegisterForm(UserCreationForm):

    username = forms.CharField(required = False, max_length = 30) #ignored
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
	    fields = ["username", "email", "password1", "password2", "user_type"]
    
    
    def clean(self, *args, **kwargs):
        """
        Normal cleanup + username generation.
        """

        cleaned_data = super(UserCreationForm, self).clean(*args, **kwargs)
        if 'email' in cleaned_data:
            cleaned_data['username'] = cleaned_data['email']

        return cleaned_data
        

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

class BarberUserSettingsForm(forms.Form):
    barbershop_name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Aslan '+_('Barbershop')
            },
        ),
        label=_('What is the name of the shop?')
    )
    address_description = forms.CharField(
        max_length=150,
        widget= forms.Textarea(
            attrs={
                'class':'form-control',
                'placeholder':'Serdivan/Sakarya',
                'rows':5
            }
        ),
        required=False,
        label=_('Address')
    )
    def save(self, user):
        try: 
            b, b_created = Barbershop.objects.get_or_create(
                name=self.cleaned_data['barbershop_name'],
                owner=user
            )
            a, a_created = address_instance = Address.objects.get_or_create(
                description=self.cleaned_data['address_description'],
                created_by=user
            )
            b.address = a
            b.save()
            if b_created:
                for sevice_name in SERVICE_NAME_CHOICES:
                    BarbershopServices.objects.create(
                        name=sevice_name[0],
                        barbershop=b
                    )
            return b
        except Exception as err:
            raise(err)


class EmployeeForm(forms.ModelForm):
    name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control mb-2 mr-sm-2',
                'placeholder':_('Name'),
                'style':'width:35%'
            },
        ),
    )
    surname = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control mb-2 mr-sm-2',
                'placeholder':_('Surname'),
                'style':'width:35%'
            },
        ),
    )
    title = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class':'init-select2 mr-sm-2',
                'style':'width:25%;'
            }
        ),
        choices=EMPLOYEE_TITLES_CHOICES
    )
    class Meta:
        model = BarbershopEmployee
        fields = ['title', 'name', 'surname']

    def save(self, barbershop):
        try:
            employee = BarbershopEmployee.objects.create(
                name=self.cleaned_data['name'],
                surname=self.cleaned_data['surname'],
                title=self.cleaned_data['title'],
                barbershop=barbershop
            )
            return employee
        except Exception as err:
            raise(err)




from django.forms import formset_factory
# EmployeeFormset = formset_factory(EmployeeForm, extra=1)
