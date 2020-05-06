from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.views import APIView

from . import serializers
from berberim.models import User, UserType, Barbershop, BarbershopService, Address, \
    BarbershopSchedule, BarbershopEmployee

from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder


class BarbershopsView(APIView):

    def get(self, request):
        print("yess you are in rest")
        # user = request.user
        barbershop_slug = request.query_params.get('barbershop_slug')
        print(barbershop_slug)

        try:
            barbershop = Barbershop.objects.get(slug=barbershop_slug)
        except Exception:
            return Response({"data": "error"})
            

        # barbershop.employees = list(barbershop.employees.all().values())
        print(list(barbershop.schedules.all().values()))
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

        return Response(data)

    
    def post(self, request):
        barbershop = request.data.get('article')

        # Create an article from the above data
        serializer = serializers.BarbershopSerializer(data=barbershop)
        if serializer.is_valid(raise_exception=True):
            barbershop = serializer.save()
        return Response({"success": "Barbershop '{}' created successfully".format(barbershop.name)})
