from django.contrib import admin
from django import forms
from .models import UserType, User, Barbershop, Address, BarbershopService, BarbershopSchedule, BarbershopEmployee, \
    Country, Province, District, BarbershopImage, Service

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from modeltranslation.admin import TranslationAdmin

class UserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class UserAdmin(UserAdmin):
    form = UserChangeForm
    list_display = ['id', 'email', 'user_type', 'created']


admin.site.register(User, UserAdmin)


class UserTypeAdminForm(forms.ModelForm):

    class Meta:
        model = UserType
        fields = '__all__'


class UserTypeAdmin(admin.ModelAdmin):
    form = UserTypeAdminForm
    list_display = ['id', 'name']
    readonly_fields = ['id', 'name']

admin.site.register(UserType, UserTypeAdmin)


class BarbershopAdminForm(forms.ModelForm):

    class Meta:
        model = Barbershop
        fields = '__all__'


class BarbershopAdmin(admin.ModelAdmin):
    form = BarbershopAdminForm
    list_display = ['name', 'slug', 'owner', 'address', 'created', 'review_rate']
    readonly_fields = ['slug', 'created']

admin.site.register(Barbershop, BarbershopAdmin)


class BarbershopEmployeeAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopEmployee
        fields = '__all__'


class BarbershopEmployeeAdmin(admin.ModelAdmin):
    form = BarbershopEmployeeAdminForm
    list_display = ['full_name', 'title', 'barbershop',  'created']

admin.site.register(BarbershopEmployee, BarbershopEmployeeAdmin)


class AddressAdminForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = '__all__'


class AddressAdmin(admin.ModelAdmin):
    form = AddressAdminForm
    list_display = ['id', 'description', 'country', 'province', 'district', 'lat', 'lng']
    readonly_fields = ['id']

admin.site.register(Address, AddressAdmin)


class CountryAdminForm(forms.ModelForm):

    class Meta:
        model = Country
        fields = '__all__'


class CountryAdmin(admin.ModelAdmin):
    form = CountryAdminForm
    list_display = ['country_code', 'country_name']

admin.site.register(Country, CountryAdmin)


class ProvinceAdminForm(forms.ModelForm):

    class Meta:
        model = Province
        fields = '__all__'


class ProvinceAdmin(admin.ModelAdmin):
    form = ProvinceAdminForm
    list_display = ['province_name']
    readonly_fields = ['province_name']

admin.site.register(Province, ProvinceAdmin)


class DistrictAdminForm(forms.ModelForm):

    class Meta:
        model = District
        fields = '__all__'


class DistrictAdmin(admin.ModelAdmin):
    form = DistrictAdminForm
    list_display = ['district_name']
    readonly_fields = ['district_name']

admin.site.register(District, DistrictAdmin)

class BarbershopServiceAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopService
        fields = '__all__'


class BarbershopServiceAdmin(admin.ModelAdmin):
    form = BarbershopServiceAdminForm
    list_display = ['id', 'service', 'price', 'duration_mins', 'barbershop', 'created']
    readonly_fields = ['created']

admin.site.register(BarbershopService, BarbershopServiceAdmin)

class BarbershopScheduleAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopSchedule
        fields = '__all__'


class BarbershopScheduleAdmin(admin.ModelAdmin):
    form = BarbershopScheduleAdminForm
    list_display = ['created', 'barbershop', 'services', 'start_time', 'end_time', 'customer', 'barbershop', 'assigned_employee']
    readonly_fields = ['created']

admin.site.register(BarbershopSchedule, BarbershopScheduleAdmin)


class BarbershopImageAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopImage
        fields = '__all__'


class BarbershopImageAdmin(admin.ModelAdmin):
    form = BarbershopImageAdminForm
    list_display = ['id', 'created', 'last_updated', 'image']
    readonly_fields = ['id', 'created', 'last_updated']

admin.site.register(BarbershopImage, BarbershopImageAdmin)


class ServiceAdminForm(forms.ModelForm):

    class Meta:
        model = Service
        fields = '__all__'


class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = ['id', 'name', 'name_en', 'created']


class MyTranslatedServiceAdmin(ServiceAdmin, TranslationAdmin):
    pass

admin.site.register(Service, MyTranslatedServiceAdmin)