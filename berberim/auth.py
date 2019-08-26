from django.conf import settings
from django.shortcuts import redirect, HttpResponse
from django.http import HttpResponse
from django.contrib import messages
import urllib.request
import urllib.error
import urllib.request as urllib2
from django.contrib.auth import authenticate, login, logout
from .models import UserType, User
from .forms import RegisterForm, LoginForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext as _
from django.shortcuts import render

def verify_logout(request):
    logout(request)

    return redirect(settings.LOGIN_URL)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if(form.is_valid()):
            print(form.cleaned_data)
            
            #try: 
            user = form.save()
            login(request, user)
            #except Exception as err:
                # if err.code == 400:
                #     messages.error(request, 'That email is already registered.')
                # else:
                #     raise
                #return HttpResponse(err)
            return redirect(settings.LOGIN_URL)

        return render(request, 'register.html', {'form': form})

    form = RegisterForm
    data = {
        'de': 'de',
        'barber_usertype_pk': UserType.objects.get(name='barber').id,
        'customer_usertype_pk': UserType.objects.get(name='customer').id
    }
    return render(request, 'register.html', {'data': data, 'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.login(request)
        
        if user is not None:
            try:
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            except Exception as err:
                # if err.code == 400:
                #     messages.error(request, 'That email is already registered.')
                # else:
                #     raise
                return HttpResponse(err)
        return render(request, 'login.html', {'form': form})


    data = {'de': 'de'}

    return render(request, 'login.html', {'data': data, 'form': form})
