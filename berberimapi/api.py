from django.shortcuts import render
from rest_framework import viewsets, permissions

from . import serializers
from berberim.models import User, UserType, Barbershop, BarbershopServices, Address, \
    BarbershopSchedule, BarbershopEmployee


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for the User class"""
    
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class UserTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the UserType class"""

    queryset = UserType.objects.all()
    serializer_class = serializers.UserTypeSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BarbershopViewSet(viewsets.ModelViewSet):
    """ViewSet for the Barbershop class"""

    queryset = Barbershop.objects.all()
    serializer_class = serializers.BarbershopSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BarbershopServicesViewSet(viewsets.ModelViewSet):
    """ViewSet for the BarbershopServices class"""

    queryset = BarbershopServices.objects.all()
    serializer_class = serializers.BarbershopServicesSerializer
    #permission_classes = [permissions.IsAuthenticated]


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet for the Address class"""

    queryset = Address.objects.all()
    serializer_class = serializers.AddressSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BarbershopScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for the BarbershopSchedule class"""

    queryset = BarbershopSchedule.objects.all()
    serializer_class = serializers.BarbershopScheduleSerializer
    #permission_classes = [permissions.IsAuthenticated]


class BarbershopEmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet for the BarbershopEmployee class"""

    queryset = BarbershopEmployee.objects.all()
    serializer_class = serializers.BarbershopEmployeeSerializer
    #permission_classes = [permissions.IsAuthenticated]
