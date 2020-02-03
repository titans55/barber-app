#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, HttpResponse

from .models import UserType, Barbershop, BarbershopSchedule, Province, District, Review, BarbershopImage,\
    Service

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.translation import gettext as _

from datetime import datetime
from dateutil import parser
from django.utils import timezone
from .forms import BarberUserSettingsForm, EmployeeForm, BarbershopServiceForm, BarbershopImageForm
from django.forms import formset_factory

from pprint import pprint
from django.views import View

from django.core import serializers
from django.db import transaction


class landing(View):

    def _get_initial_data(self, is_filtered, default_filtered_address, user):
        if default_filtered_address is not None:
            province_code = default_filtered_address['province_code']
            district_code = default_filtered_address['district_code']
            try:
                barbershops = Barbershop.objects.filter(address__province__province_code=province_code, address__district__district_code=district_code)
            except:
                barbershops = None
        else:
            barbershops  = None
        data = {
            'barbershops': barbershops,
            'filters': {
                'filtered': is_filtered,
                'provinces': Province.objects.all().order_by('province_code'),
                'districts': District.objects.order_by('district_code'),
                'default_filtered_address': default_filtered_address
            }
        }
        if user.is_anonymous is False:
            if 'customer' == str(user.user_type):
                
                pass
        return data

    def get(self, request, **kwargs):
        user = request.user
        province = kwargs.get('province', None)
        district = kwargs.get('district', None)
        default_filtered_address = request.session.get('default_filtered_address')
        print("wololo", user)

        if user.is_anonymous:
            if province and district:
                data = self._get_initial_data(True, default_filtered_address, user)

                return render(request, 'customer' + '/dashboard.html',
                            {'data': data, 'user': user})
            else: 
                if default_filtered_address:
                    province_name = Province.objects.get(province_code=default_filtered_address['province_code']).province_name.lower()
                    district_name = District.objects.get(district_code=default_filtered_address['district_code']).district_name.lower()
                    return redirect('landing-with-province-n-district', province=province_name, district=district_name)
                
                data = self._get_initial_data(False, default_filtered_address, user)
                return render(request, 'customer' + '/dashboard.html',
                            {'data': data, 'user': user})

        else: 
            if 'barber' == str(user.user_type):
                print("wololo")
                try:
                    barbershop = Barbershop.objects.get(owner=user)
                    data = {
                        'barbershop': barbershop,
                    }
                except Barbershop.DoesNotExist:
                    return redirect('user-settings')


            elif 'customer' == str(user.user_type):
                if province and district:
                    data = self._get_initial_data(True, default_filtered_address, user)
                else:
                    print("aha")
                    if default_filtered_address:
                        province_name = Province.objects.get(province_code=default_filtered_address['province_code']).province_name.lower()
                        district_name = District.objects.get(district_code=default_filtered_address['district_code']).district_name.lower()
                        return redirect('landing-with-province-n-district', province=province_name, district=district_name)
                    
                    data = self._get_initial_data(False, default_filtered_address, user)
                    print("yess")
                    print(user.user_type)
                
            
            return render(request, str(user.user_type) + '/dashboard.html',
                        {'data': data, 'user': user})

    def _get_current_coordinates(self):
        pass


@login_required
def review_barbershop_ajax(request):
    user = request.user
    schedule_id = int(request.POST['schedule_id'])
    review_rate = float(request.POST['review_rate'])*2.0
    comments = request.POST['comments']
    if not comments: comments = None 

    try:
        schedule = BarbershopSchedule.objects.get(id=schedule_id)
    except BarbershopSchedule.DoesNotExist:
        return JsonResponse({
            "status" : "fail",
        })
    
    if schedule.customer == user and not schedule.reviewed:
        barbershop = schedule.barbershop
        with transaction.atomic():
            Review.objects.create(
                reviewer = user,
                reviewed_schedule_id = schedule_id,
                reviewed_barbershop_id = barbershop.id,
                review_rate = review_rate,
                comments = comments
            )
            barbershop.set_new_review_rate(review_rate) 
            schedule.reviewed = True
            schedule.save()

        return JsonResponse({
            "status" : "success",
        })
    else:
        return JsonResponse({
            "status": "fail"
        })

def select_province_district(request):
    province_code = request.POST['province_code']
    district_code = request.POST['district_code']

    province_name = Province.objects.get(province_code=province_code).province_name.lower()
    district_name = District.objects.get(district_code=district_code).district_name.lower()

    request.session['default_filtered_address'] = {
        "province_code": province_code,
        "district_code": district_code
    }
    return redirect('landing-with-province-n-district', province=province_name, district=district_name) 

class user_settings_view(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        barbershop_active_services = []
        services = [
            {
                "pk": srv.pk,
                "name": srv.name,
                "is_active": False
            } for srv in Service.objects.all()
        ]
        if 'barber' == str(user.user_type):
            if not Barbershop.objects.filter(owner=user).exists():
                form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra()
                return render(
                    request,
                    str(user.user_type) + '/settings.html',
                    {
                        'user': user,
                        'barbershop_form': form,
                        'extra': extra,
                        'services': services,
                        'barbershop_active_services': barbershop_active_services
                    }
                )
            else: 
                barbershop_active_services = Barbershop.objects.filter(owner=user).first().active_services
                for srv in services:
                    if srv['pk'] in (bas.pk for bas in barbershop_active_services):
                        srv['is_active'] = True

            form, employee_formset, barbershop_services_formset, extra = self._init_forms_and_extra()
            # print(barbershop_services_formset)
            return render(
                request,
                str(user.user_type) + '/settings.html',
                {
                    'user': user,
                    'barbershop_form': form,
                    'employee_formset': employee_formset,
                    'barbershop_services_formset':barbershop_services_formset,
                    'extra': extra,
                    'services': services,
                    'barbershop_active_services': barbershop_active_services
                }
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
                BarbershopServicesFormset = formset_factory(BarbershopServiceForm, extra=0)
                barbershop_services_formset = BarbershopServicesFormset(
                    request_post,
                    initial=[{'id':serv.id, 'service': serv.service, 'price': serv.price, 'duration_mins': serv.duration_mins} for serv in barbershop.services.all().order_by('id')],
                    prefix='barbershop_services'
                )
            else:
                raise Exception('Barbershop services doesnt exists, please contact dev team.')

        except Barbershop.DoesNotExist as err:
            form = BarberUserSettingsForm(request_post)
            extra = 1 if extra is None else extra
            employee_formset = formset_factory(EmployeeForm, extra=extra)(request_post, prefix='employees')

            BarbershopServicesFormset = formset_factory(BarbershopServiceForm, extra=3)
            barbershop_services_formset = BarbershopServicesFormset(
                request_post, prefix='barbershop_services'
            )
        
        return form, employee_formset, barbershop_services_formset, extra
    
class userSettingsAddPhoto(View):
    @method_decorator(login_required)
    def get(self, request):
        user = self.request.user
        try:
            barbershop = Barbershop.objects.get(owner=user)
        except Barbershop.DoesNotExist:
            return "Barbershop doesnt exist"
        
        data = {
            "barbershop_images": barbershop.images
        }
        return render(request, str(user.user_type) + '/add-photos.html', {'data': data})


    @method_decorator(login_required)
    def post(self, request):
        user = self.request.user
        image = request.FILES.get("image-input")
        barbershop = Barbershop.objects.get(owner=user)
        barbershop_image = BarbershopImage(
            uploaded_by=user,
            image=image,
            barbershop=barbershop
        )
        form = BarbershopImageForm(
            instance=barbershop_image
        )
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            print("asddsa")
        return render(request, str(user.user_type) + '/add-photos.html', {'form': form})

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
                'services': list(barbershop.services.all()),
                'employees': list(barbershop.employees.all().values()),
                'schedules': json.loads(json.dumps(list(barbershop.schedules.filter(start_time__day=now.day).values(
                    'start_time__hour', 'start_time__minute', 'end_time__hour', 'end_time__minute', 'assigned_employee'
                    )), cls=DjangoJSONEncoder))
            }
        }
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

class barbershop_profile(View):

    def get(self, request, barbershop_slug):
        user = request.user
        try:
            barbershop = Barbershop.objects.get(slug=barbershop_slug)
        except:
            return HttpResponseNotFound("hello")   



        data = {
            "barbershop": barbershop
        }
        return render(request, 'common/barbershop_profile.html', context=data)