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
                extra = 0 if extra is None else extra
                EmployeeFormSet = formset_factory(EmployeeForm, extra=extra)
                employee_formset = EmployeeFormSet(
                    request_post,
                    initial=[{'title': emp.title, 'name': emp.name, 'surname': emp.surname} for emp in barbershop.employees.all()]
                )
            else:
                extra = 1 if extra is None else extra
                employee_formset = formset_factory(EmployeeForm, extra=extra)(request_post)

            if barbershop.services.exists():
                BarbershopServicesFormset = formset_factory(BarbershopServicesForm, extra=0)
                barbershop_services_formset = BarbershopServicesFormset(
                    request_post,
                    initial=[{'name': serv.name, 'price': serv.price, 'duration_mins': serv.duration_mins} for serv in barbershop.services.all().order_by('id')]
                )
            else:
                raise Exception('Barbershop services doesnt exists, please contact dev team.')

        except Barbershop.DoesNotExist:
            form = BarberUserSettingsForm(request_post)
            extra = 1 if extra is None else extra
            employee_formset = formset_factory(EmployeeForm, extra=extra)(request_post)

            BarbershopServicesFormset = formset_factory(BarbershopServicesForm, extra=3)
            barbershop_services_formset = BarbershopServicesFormset(
                request_post
            )
        
        return form, employee_formset, barbershop_services_formset, extra

    if 'barber' == str(user.user_type):
        if request.method == 'POST':
            if request.POST['action'] == "+":
                extra = int(float(request.POST['extra']))
                form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra(extra + 1)
            else:
                extra = int(float(request.POST['extra']))
                form, employee_formset, barbershop_services_formset, extra_old = _init_forms_and_extra(extra, request.POST)
                if form.is_valid() and employee_formset.is_valid() and barbershop_services_formset.is_valid():
                    if request.POST['action'] == "Create":
                        print (form.changed_data, " form.changed data")
                        barbershop = None
                        if len(form.changed_data) > 0:
                            barbershop = form.save(user)
                        for form_employee in employee_formset:
                            print (form_employee.changed_data, " form_employee.changed data")
                            if not 'delete' in form_employee.cleaned_data:
                                if len(form_employee.changed_data) > 0:
                                    barbershop = Barbershop.objects.get(owner=user) if barbershop is None else barbershop
                                    form_employee.save(barbershop)
                                    extra=0
                        for form_barbershop_service in barbershop_services_formset:
                            print (form_barbershop_service.changed_data, " form_barbershop_service.changed data")
                            if not 'delete' in form_barbershop_service.cleaned_data:
                                if len(form_barbershop_service.changed_data) > 0:
                                    barbershop = Barbershop.objects.get(owner=user) if barbershop is None else barbershop
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
                {'user': user, 'form': form, 'employee_formset':employee_formset,
                'barbershop_services_formset':barbershop_services_formset, 'extra': extra}
            )
        
        form, employee_formset, barbershop_services_formset, extra = _init_forms_and_extra()

        return render(
            request,
            str(user.user_type) + '/settings.html',
            {'user': user, 'form': form, 'employee_formset':employee_formset,
            'barbershop_services_formset':barbershop_services_formset, 'extra': extra}
        )


    return render(request, str(user.user_type) + '/settings.html', {'data': data})

@login_required
def map(request):
    user = request.user

    data = {'de': 'de'}

    return render(request, str(user.user_type) + '/map.html', {'data': data})

@login_required
def barbershop(request, barbershop_slug):
    print(barbershop_slug)
    user = request.user

    try:
        barbershop = Barbershop.objects.get(slug=barbershop_slug)
    except:
        return HttpResponseNotFound("hello")    

    # barbershop.employees = list(barbershop.employees.all().values())
    print(list(barbershop.schedules.all().values()))
    now = timezone.localtime(timezone.now())

    data = {
        'barbershop': {
            'name': barbershop.name,
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
