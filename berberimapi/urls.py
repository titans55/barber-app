# myapi/urls.py
from django.urls import include, path
from rest_framework import routers
from . import api
from .api_views import BarbershopsView

router = routers.DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'usertype', api.UserTypeViewSet)
router.register(r'barbershop', api.BarbershopViewSet)
router.register(r'barbershopservices', api.BarbershopServicesViewSet)
router.register(r'address', api.AddressViewSet)
router.register(r'barbershopschedule', api.BarbershopScheduleViewSet)
router.register(r'barbershopemployee', api.BarbershopEmployeeViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('models/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('barbershop', BarbershopsView.as_view()),

]