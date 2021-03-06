from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserType, Barbershop, BarbershopEmployee, EMPLOYEE_TITLES_CHOICES,\
    SERVICE_NAME_CHOICES, Address, BarbershopService, Country, Province, District, BarbershopImage,\
    Service
from django.utils.translation import gettext as _
import re
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate


alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.') 
#TODO make validators work, For example you can assign numeric values to employee names currently


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
        

class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg border-left-0'})
    )
    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user: #TODO or not user.is_active
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        return user

class BarberUserSettingsForm(forms.Form):
    barbershop_id = forms.IntegerField(
        widget=forms.HiddenInput(),
        disabled=True,
        required=False #so we can create barbershop on first login
    )
    barbershop_name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Aslan '+_('Barbershop')
            },
        ),
        label=_('What is the name of the shop?')
    )
    address_country = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class':'init-select2 ml-1',
                'style':'width:32%;'
            }
        ),
        choices=[(c.country_code, c.country_name) for c in Country.objects.all()],
        initial=Country.objects.get(country_code="TR"),
        label=""
    )
    address_province = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class':'init-select2',
                'style':'width:32%;'

            }
        ),
        choices=[(p.province_code, p.province_name) for p in Province.objects.all().order_by('province_code')],
        label=""
    )
    address_district = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class':'init-select2',
                'style':'width:32%;'
            }
        ),
        choices=[(d.district_code, d.district_name) for d in District.objects.order_by('district_code')],
        label=""
    )
    address_description = forms.CharField(
        max_length=150,
        widget= forms.Textarea(
            attrs={
                'class':'form-control',
                'placeholder':'Mahalle/Cadde/Sokak, Bina/Daire No.',
                'rows':2
            }
        ),
        required=False,
        label=_('Address')
    )
    about = forms.CharField(
        max_length=1000,
        widget= forms.Textarea(
            attrs={
                'class':'form-control',
                'rows':5
            }
        ),
        required=False,
        label=_("Fill the 'about' section which would display in barbershop profile page")
    )
    address_lat = forms.DecimalField(
        decimal_places=6,
        widget=forms.HiddenInput(),
    )
    address_lng = forms.DecimalField(
        decimal_places=6,
        widget=forms.HiddenInput(),
    )

    def save(self, user):

        try:
            if self.cleaned_data['barbershop_id'] is None:
                raise(Barbershop.DoesNotExist)

            barbershop = Barbershop.objects.get(
                id=self.cleaned_data['barbershop_id'],
                owner=user
            )
            barbershop.name = self.cleaned_data['barbershop_name']
            barbershop.about = self.cleaned_data['about']
            barbershop.save()

            barbershop.address.country = Country.objects.get(country_code=self.cleaned_data['address_country'])
            barbershop.address.province = Province.objects.get(province_code=self.cleaned_data['address_province'])
            barbershop.address.district = District.objects.get(district_code=self.cleaned_data['address_district'])
            barbershop.address.description = self.cleaned_data['address_description'] if self.cleaned_data['address_description'].strip() else None
            barbershop.address.lat = self.cleaned_data['address_lat']
            barbershop.address.lng = self.cleaned_data['address_lng']
            barbershop.address.save()

            return barbershop
            
        except Barbershop.DoesNotExist as err:

            barbershop = Barbershop.objects.create(
                name=self.cleaned_data['barbershop_name'],
                owner=user,
            )

            for sevice_name in SERVICE_NAME_CHOICES:
                BarbershopService.objects.create(
                    name=sevice_name[0],
                    barbershop=barbershop
                )

            address = Address.objects.create(
                country = Country.objects.get(country_code=self.cleaned_data['address_country']),
                province = Province.objects.get(province_code=self.cleaned_data['address_province']),
                district = District.objects.get(district_code=self.cleaned_data['address_district']),
                description=self.cleaned_data['address_description'],
                lat=self.cleaned_data['address_lat'],
                lng=self.cleaned_data['address_lng'],
                created_by=user
            )
            barbershop.address = address
            barbershop.save()
            
            return barbershop

        # try: 
        #     b, b_created = Barbershop.objects.get_or_create(
        #         name=self.cleaned_data['barbershop_name'],
        #         owner=user
        #     )
        #     a, a_created = address_instance = Address.objects.get_or_create(
        #         description=self.cleaned_data['address_description'],
        #         created_by=user
        #     )
        #     b.address = a
        #     b.save()
        #     if b_created:
        #         for sevice_name in SERVICE_NAME_CHOICES:
        #             BarbershopServices.objects.create(
        #                 name=sevice_name[0],
        #                 barbershop=b
        #             )
        #     return b
        # except Exception as err:
        #     raise(err)


class EmployeeForm(forms.ModelForm):
    id = forms.IntegerField(
        widget= forms.NumberInput(attrs={'class':'d-none', 'readonly':'readonly'}),
        disabled=True,
        required=False #so we can create employee
    )

    name = forms.CharField(
        widget= forms.TextInput(
            attrs={
                'class':'form-control mb-2 mr-sm-2',
                'placeholder':_('Name'),
                'style':'width:35%',
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
        fields = ['id', 'title', 'name', 'surname']

    def save(self, barbershop):
        try:
            if self.cleaned_data['id'] is None:
                raise(BarbershopEmployee.DoesNotExist)

            employee = BarbershopEmployee.objects.filter(
                id=self.cleaned_data['id'],
            ).update(**self.cleaned_data)

            return employee
        except BarbershopEmployee.DoesNotExist as err:

            employee = BarbershopEmployee.objects.create(
                name=self.cleaned_data['name'],
                surname=self.cleaned_data['surname'],
                title=self.cleaned_data['title'],
                barbershop=barbershop
            )

            return employee


class BarbershopServiceForm(forms.ModelForm):
    id = forms.IntegerField(
        widget= forms.NumberInput(attrs={'class':'d-none', 'readonly':'readonly'}),
        disabled=True,
        required=False #so we can create service
    )
    service = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                'class':'init-select2 form-control text-center',
                'readonly': 'readonly'
            }
        ),
        queryset=Service.objects.all(),
    )
    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control text-center'})
    )
    duration_mins = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class':'form-control text-center'})
    )
    class Meta:
        model = BarbershopService
        fields = ['id', 'service', 'price', 'duration_mins']        

    def save(self, barbershop):
        try:
            if self.cleaned_data['id'] is None:
                raise(BarbershopService.DoesNotExist)

            barbershop_service = BarbershopService.objects.filter(
                id=self.cleaned_data['id'],
            ).update(**self.cleaned_data)

            return barbershop_service
        except BarbershopService.DoesNotExist as err:
            if BarbershopService.objects.filter(barbershop=barbershop, service_id=self.cleaned_data['service']).exists():
                raise Exception("Service for that barbershop is already exists")

            barbershop_service = BarbershopService.objects.create(
                service=self.cleaned_data['service'],
                price=self.cleaned_data['price'],
                duration_mins=self.cleaned_data['duration_mins'],
                barbershop=barbershop
            )
            return barbershop_service

class BarbershopImageForm(forms.ModelForm):
    class Meta:
        model = BarbershopImage
        fields = ('image', 'uploaded_by', 'barbershop')