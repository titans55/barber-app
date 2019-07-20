from django.urls import path, include
from berberproje import settings
from . import views, auth

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login', auth.login_view, name='login'),

    #customer
    path('barbershop-map', views.map, name='barbershop-map'),
    path('barbershop/<slug:barbershop_slug>', views.barbershop, name='barbershop'),
    path('user-settings', views.user_settings, name='user-settings'),


    #AJAX CALL


    #FORM CALL
    path('schedule', views.schedule_customer, name='schedule'),


    #AUTH
    path('logout', auth.verify_logout, name='logout'),
    path('register', auth.register, name='register'),


]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns