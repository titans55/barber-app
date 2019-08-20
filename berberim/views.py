#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, HttpResponse

from .models import UserType, Barbershop, BarbershopSchedule, Province, District

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.translation import gettext as _

from datetime import datetime
from dateutil import parser
from django.utils import timezone
from .forms import BarberUserSettingsForm, EmployeeForm, BarbershopServicesForm
from django.forms import formset_factory

from pprint import pprint
from django.views import View

from django.core import serializers


class landing(View):

    def get(self, request, **kwargs):
        user = request.user
        province = kwargs.get('province', None)
        district = kwargs.get('district', None)
        default_filtered_address = request.session.get('default_filtered_address')

        if user.is_anonymous:
            if province and district:
                barbershops = Barbershop.objects.all()
                data = {
                    'barbershops': barbershops,
                    'filters': {
                        'filtered': True,
                        'provinces': Province.objects.all().order_by('province_code'),
                        'districts': District.objects.order_by('district_code'),
                        'default_filtered_address': default_filtered_address
                    }
                }
                return render(request, 'customer' + '/dashboard.html',
                            {'data': data, 'user': user})
            else: 
                if default_filtered_address:
                    province_name = Province.objects.get(province_code=default_filtered_address['province_code']).province_name.lower()
                    district_name = District.objects.get(district_code=default_filtered_address['district_code']).district_name.lower()
                    return redirect('landing-with-province-n-district', province=province_name, district=district_name)
                barbershops = Barbershop.objects.all()
                data = {
                    'barbershops': barbershops,
                    'filters': {
                        'filtered': False,
                        'provinces': Province.objects.all().order_by('province_code'),
                        'districts': District.objects.order_by('district_code'),
                        'default_filtered_address': default_filtered_address
                    }
                }
                return render(request, 'customer' + '/dashboard.html',
                            {'data': data, 'user': user})

        else: 
            self._get_current_coordinates()
            if 'barber' == str(user.user_type):
                try:
                    barbershop = Barbershop.objects.get(owner=user)
                    data = {
                        'barbershop': barbershop
                    }
                except Barbershop.DoesNotExist:
                    return redirect('user-settings')


            elif 'customer' == str(user.user_type):
                barbershops = Barbershop.objects.all()
                data = {'barbershops': barbershops}
                
            
            return render(request, str(user.user_type) + '/dashboard.html',
                        {'data': data, 'user': user})

    def _get_current_coordinates(self):
        pass


def select_province_district(request):
    province_code = request.POST['province_code']
    district_code = request.POST['district_code']

    province_name = Province.objects.get(province_code=province_code).province_name.lower()
    district_name = District.objects.get(district_code=district_code).district_name.lower()

    request.session['default_filtered_address'] = {
        "province_code": province_code,
        "district_code": district_code
    }
    return redirect('landing-with-province-n-district', province=province_name, district=district_name)  # 4

class user_settings_view(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user

        if 'barber' == str(user.user_type):
            if not Barbershop.objects.filter(owner=user).exists():
                form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra()
                return render(
                    request,
                    str(user.user_type) + '/settings.html',
                    {'user': user, 'barbershop_form': form, 'extra': extra}
                )


            form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra()
            # print(barbershop_services_formset)
            return render(
                request,
                str(user.user_type) + '/settings.html',
                {'user': user, 'barbershop_form': form, 'employee_formset': employee_formset,
                'barbershop_services_formset':barbershop_services_formset, 'extra': extra}
            )
        else:
            pass

    @method_decorator(login_required)
    def post(self, request):
        user = request.user

        extra = int(float(request.POST['extra'])) if Barbershop.objects.filter(owner=user).exists() else None
        form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra(extra, request.POST)

        if not Barbershop.objects.filter(owner=user).exists():
            form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra(None, request.POST) #TODO can we remove this line?
            if form.is_valid():
                barbershop = form.save(user)
                form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra()



        elif form.is_valid() and employee_formset.is_valid() and barbershop_services_formset.is_valid():

            print("form.is_valid() ", form.is_valid())
            print("employee_formset.is_valid() ", employee_formset.is_valid())
            print("barbershop_services_formset.is_valid ", barbershop_services_formset.is_valid())

            if request.POST['action'] == "Create":
            #    print (form.changed_data, " form.changed data")
                barbershop = None
                if len(form.changed_data) > 0:
                    barbershop = form.save(user)
                for form_employee in employee_formset:
                    #   print (form_employee.changed_data, " form_employee.changed data")
                    if not 'delete' in form_employee.cleaned_data:
                        if len(form_employee.changed_data) > 0:
                            barbershop = barbershop if barbershop is not None else Barbershop.objects.get(owner=user)
                            form_employee.save(barbershop)
                            extra=0
                for form_barbershop_service in barbershop_services_formset:
                #     print (form_barbershop_service.changed_data, " form_barbershop_service.changed data")
                    if not 'delete' in form_barbershop_service.cleaned_data:
                        if len(form_barbershop_service.changed_data) > 0:
                            barbershop = barbershop if barbershop is not None else Barbershop.objects.get(owner=user)
                            form_barbershop_service.save(barbershop)
                            
            elif request.POST['action'] == "Edit":
                for form_employee in employee_formset:
                    if 'delete' in form_employee.cleaned_data and form_employee.cleaned_data['delete']:
                        pass
                        # delete data
                    else:
                        pass
                        # create data
                
        return render(
            request,
            str(user.user_type) + '/settings.html',
            {'user': user, 'barbershop_form': form, 'employee_formset': employee_formset,
            'barbershop_services_formset':barbershop_services_formset, 'extra':extra}
        )

    def _get_barbershop_user_settings_form_initial_data(self, barbershop):
        return {
            'barbershop_id': barbershop.id,
            'barbershop_name': barbershop.name,
            'address_country': barbershop.address.country.country_code,
            'address_province': barbershop.address.province.province_code,
            'address_district': barbershop.address.district.district_code,
            'address_description': barbershop.address.description,
            'address_lat': barbershop.address.lat,
            'address_lng': barbershop.address.lng,
        }

    def _init_forms_and_extra(self, extra=None, request_post=None):
        #request_post is None on Get Requests
        user = self.request.user

        try:
            barbershop = Barbershop.objects.get(owner=user)

            form = BarberUserSettingsForm(
                request_post,
                initial=self._get_barbershop_user_settings_form_initial_data(barbershop)
            )
            if barbershop.employees.exists():
                #TODO optimize this
               # print(extra, " = > extra")
                extra = 0 if extra is None else extra
               # print(extra, " => extra before formset")
                EmployeeFormSet = formset_factory(EmployeeForm, extra=extra)
                #print(EmployeeFormSet)
               # print(len(barbershop.employees.all()), "len barbershop.employees.all()")
                employee_formset = EmployeeFormSet(
                    request_post,
                    initial=[{'id': emp.id, 'title': emp.title, 'name': emp.name, 'surname': emp.surname} for emp in barbershop.employees.all()],
                    prefix='employees'
                )
                # print(len(employee_formset), "len of employee_formset")
            else:
                extra = 1 if extra is None else extra
                employee_formset = formset_factory(EmployeeForm, extra=extra)(request_post)

            if barbershop.services.exists():
                BarbershopServicesFormset = formset_factory(BarbershopServicesForm, extra=0)
                barbershop_services_formset = BarbershopServicesFormset(
                    request_post,
                    initial=[{'id':serv.id, 'name': serv.name, 'price': serv.price, 'duration_mins': serv.duration_mins} for serv in barbershop.services.all().order_by('id')],
                    prefix='barbershop_services'
                )
            else:
                raise Exception('Barbershop services doesnt exists, please contact dev team.')

        except Barbershop.DoesNotExist as err:
            form = BarberUserSettingsForm(request_post)
            extra = 1 if extra is None else extra
            employee_formset = formset_factory(EmployeeForm, extra=extra)(request_post, prefix='employees')

            BarbershopServicesFormset = formset_factory(BarbershopServicesForm, extra=3)
            barbershop_services_formset = BarbershopServicesFormset(
                request_post, prefix='barbershop_services'
            )
        
        return form, employee_formset, barbershop_services_formset, extra
    
def load_districts_ajax(request):
    if request.method == "POST":
        province_code = request.POST.get("province_code")
        province = Province.objects.get(province_code=province_code)
        districts = District.objects.filter(province=province)
        districts = serializers.serialize("json", districts)
        
        return HttpResponse(districts, content_type='application/json')
    

@login_required
def map(request):
    user = request.user

    barbershops = Barbershop.objects.all()
    # barbershops = serializers.serialize('json', barbershops)

    data = {'barbershops': barbershops}

    return render(request, str(user.user_type) + '/map.html', {'data': data})

class barbershop_view(View):

    @method_decorator(login_required)
    def get(self, request, barbershop_slug):
        user = request.user

        try:
            barbershop = Barbershop.objects.get(slug=barbershop_slug)
        except:
            return HttpResponseNotFound("hello")    

        now = timezone.localtime(timezone.now())

        data = {
            'barbershop': {
                'name': barbershop.name,
                'slug': barbershop.slug,
                'id': barbershop.id,
                'services': list(barbershop.services.all().values()),
                'employees': list(barbershop.employees.all().values()),
                'schedules': list(barbershop.schedules.filter(start_time__day=now.day).values(
                    'start_time__hour', 'start_time__minute', 'end_time__hour', 'end_time__minute', 'assigned_employee'
                    ))
            }
        }
        data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
        print(data)
        return render(request, str(user.user_type) + '/barbershop.html', data)

    @method_decorator(login_required)
    def post(self, request, barbershop_slug=None):
        user = request.user

        start_time = parser.parse(request.POST['startTime'])
        end_time = parser.parse(request.POST['endTime'])
        services = request.POST['services'].split(',')
        employee_id = request.POST['employeeID']
        barbershop_id = request.POST['barbershopID']

        try:
            BarbershopSchedule.objects.create(
                start_time=start_time,
                end_time=end_time,
                services=services,
                barbershop_id=barbershop_id,
                assigned_employee_id=employee_id,
                customer=request.user
            )
        except Exception as err:
            raise err
        return redirect("landing")
