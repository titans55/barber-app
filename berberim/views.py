#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseNotFound

from .models import UserType, Barbershop

from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils.translation import gettext as _

# Create your views here.

@login_required
def landing(request):
    user = request.user
    # TODO filter barbershops by distance

    barbarshops = Barbershop.objects.all()
    print(barbarshops)
    data = {'barbershops': barbarshops}

    return render(request, str(user.user_type) + '/dashboard.html',
                  {'data': data})

@login_required
def user_settings(request):
    user = request.user

    data = {'de': 'de'}

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
    data = {
        'barbershop': {
            'name': barbershop.name,
            'services': list(barbershop.services.all().values()),
            'employees': list(barbershop.employees.all().values()),
        }
    }
    data = json.loads(json.dumps(data, cls=DjangoJSONEncoder))
    print(data)
    return render(request, str(user.user_type) + '/barbershop.html', data)

@login_required
def schedule_customer(request):
    user = request.user

    pass
