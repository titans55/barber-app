#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, HttpResponse

from .models import UserType, Barbershop, BarbershopSchedule

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
import slumber
import requests

@login_required
def landing(request):
    user = request.user
    # TODO filter barbershops by distance

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

@login_required
def user_settings(request):
    user = request.user
    
    def _get_barbershop_user_settings_form_initial_data(barbershop):
        return {
            'barbershop_name':barbershop.name,
            'address_description':barbershop.address.description
        }

    def _init_forms_and_extra(extra=None, request_post=None):
        #request_post is None on Get Requests
        try:
            barbershop = Barbershop.objects.get(owner=user)

            form = BarberUserSettingsForm(
                request_post,
                initial=_get_barbershop_user_settings_form_initial_data(barbershop)
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

    if 'barber' == str(user.user_type):
        if request.method == 'POST':
            extra = int(float(request.POST['extra'])) if Barbershop.objects.filter(owner=user).exists() else None
            form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra(extra, request.POST)

            if not Barbershop.objects.filter(owner=user).exists():
                form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra(None, request.POST) #TODO can we remove this line?
                if form.is_valid():
                    barbershop = form.save(user)
                    form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra()



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
                {'user': user, 'form': form, 'employee_formset': employee_formset,
                'barbershop_services_formset':barbershop_services_formset, 'extra':extra}
            )
        
        elif request.method == 'GET':
            if not Barbershop.objects.filter(owner=user).exists():
                form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra()
                return render(
                    request,
                    str(user.user_type) + '/settings.html',
                    {'user': user, 'form': form, 'extra': extra}
                )


            form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra()
            # print(barbershop_services_formset)
            return render(
                request,
                str(user.user_type) + '/settings.html',
                {'user': user, 'form': form, 'employee_formset': employee_formset,
                'barbershop_services_formset':barbershop_services_formset, 'extra': extra}
            )

    else:
        pass

@login_required
def map(request):
    user = request.user

    data = {'de': 'de'}

    return render(request, str(user.user_type) + '/map.html', {'data': data})

@login_required
def barbershop(request, barbershop_slug):

    response = requests.get('http://localhost:8000/api/barbershops', params={'barbershop_slug':barbershop_slug})
    data = json.loads(json.dumps(response.json(), cls=DjangoJSONEncoder))
    print(data)
   
    return render(request, str('customer') + '/barbershop.html', data)

@login_required
def schedule_customer(request):
    user = request.user

    start_time = parser.parse(request.POST['startTime'])
    end_time = parser.parse(request.POST['endTime'])
    services = request.POST['services'].split(',')
    employee_id = request.POST['employeeID']
    barbershop_id = request.POST['barbershopID']
    print(start_time, "wololo")

    print(services)
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
