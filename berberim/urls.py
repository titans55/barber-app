from django.urls import path, include
from berberproje import settings
from . import views, auth

urlpatterns = [
    path('', views.landing.as_view(), name='landing'),
    path('<province>/<district>-berberler', views.landing.as_view(), name='landing-with-province-n-district'),
    path('select-province-district', views.select_province_district, name='selectProvinceDistrict'),
    path('review_barbershop_ajax', views.review_barbershop_ajax, name='review-barbershop-ajax'), #AJAX CALL from landing-with-province-n-district page


    #customer
    path('barbershop-map', views.map, name='barbershop-map'),
    path('barbershop/<slug:barbershop_slug>', views.barbershop_view.as_view(), name='barbershop'),
    path('user-settings', views.user_settings_view.as_view(), name='user-settings'),
    path('load-districts', views.load_districts_ajax), #AJAX CALL from user-settings page






    #AUTH
    path('login', auth.login_view, name='login'),
    path('logout', auth.verify_logout, name='logout'),
    path('register', auth.register, name='register'),


]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns