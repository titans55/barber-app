from rest_framework import serializers
from berberim import models

class UserSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = models.User
        fields = ("url", "id", "email", "password", "user_type")


class UserTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserType
        fields = (
            'pk', 
            'id', 
            'name', 
        )


class BarbershopSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Barbershop
        fields = (
            'slug', 
            'id', 
            'name', 
            'created', 
        )


class BarbershopServicesSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BarbershopServices
        fields = (
            'pk', 
            'name', 
            'price', 
            'duration_mins', 
            'created', 
        )


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Address
        fields = (
            'pk', 
            'id', 
            'description', 
            'lng', 
            'lat', 
        )


class BarbershopScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BarbershopSchedule
        fields = (
            'pk', 
            'created', 
            'services', 
            'start_time', 
            'end_time', 
        )


class BarbershopEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.BarbershopEmployee
        fields = (
            'pk', 
            'name', 
            'created', 
            'surname', 
            'title', 
        )
