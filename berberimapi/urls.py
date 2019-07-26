# myapi/urls.py
from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'usertype', views.UserTypeViewSet)
router.register(r'barbershop', views.BarbershopViewSet)
router.register(r'barbershopservices', views.BarbershopServicesViewSet)
router.register(r'address', views.AddressViewSet)
router.register(r'barbershopschedule', views.BarbershopScheduleViewSet)
router.register(r'barbershopemployee', views.BarbershopEmployeeViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]