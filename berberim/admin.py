from django.contrib import admin
from django import forms
from .models import UserType, User, Barbershop, Address, BarbershopServices, BarbershopSchedule, BarbershopEmployee

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

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
    list_display = ['name', 'slug', 'owner', 'address', 'created']
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
    list_display = ['id', 'description', 'lat', 'lng']
    readonly_fields = ['id']

admin.site.register(Address, AddressAdmin)

class BarbershopServicesAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopServices
        fields = '__all__'


class BarbershopServicesAdmin(admin.ModelAdmin):
    form = BarbershopServicesAdminForm
    list_display = ['name', 'price', 'duration_mins', 'barbershop', 'created']
    readonly_fields = ['created']

admin.site.register(BarbershopServices, BarbershopServicesAdmin)

class BarbershopScheduleAdminForm(forms.ModelForm):

    class Meta:
        model = BarbershopSchedule
        fields = '__all__'


class BarbershopScheduleAdmin(admin.ModelAdmin):
    form = BarbershopScheduleAdminForm
    list_display = ['created', 'barbershop', 'services', 'start_time', 'end_time']
    readonly_fields = ['created']

admin.site.register(BarbershopSchedule, BarbershopScheduleAdmin)