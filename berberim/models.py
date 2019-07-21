from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import AutoField
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import EmailField
from django.db.models import IntegerField
from django.db.models import PositiveIntegerField
from django.db.models import SmallIntegerField
from django.db.models import TextField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth import models as auth_models
from django.db import models as models
from django_extensions.db import fields as extension_fields
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _

class User(AbstractUser):

    # Fields
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Relationship Fields
    user_type = models.ForeignKey(
        'berberim.UserType',
        on_delete=models.CASCADE, related_name="users", 
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_type']

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.email

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_user_detail', args=(self.slug,))

    def get_update_url(self):
        return reverse('berberim_user_update', args=(self.slug,))


class UserType(models.Model):

    # Fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_usertype_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('berberim_usertype_update', args=(self.pk,))


class Barbershop(models.Model):

    # Fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = extension_fields.AutoSlugField(unique=True, populate_from='name', blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Relationship Fields
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="barbershops", 
    )
    address = models.OneToOneField(
       'berberim.Address',
        on_delete=models.CASCADE, related_name="barbershops_2", null=True, blank=True
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.slug

    def get_absolute_url(self):
        return reverse('berberim_barbershop_detail', args=(self.slug,))


    def get_update_url(self):
        return reverse('berberim_barbershop_update', args=(self.slug,))

#Expand this array by customer demand
EMPLOYEE_TITLES_CHOICES = [
    ('Master', _('Master')),
    ('Journeyman', _('Journeyman')),
    ('Apprentice', _('Apprentice')),
]

class BarbershopEmployee(models.Model):

    # Fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    title = models.CharField(max_length=30, choices=EMPLOYEE_TITLES_CHOICES)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Relationship Fields
    barbershop = models.ForeignKey(
        'berberim.Barbershop',
        on_delete=models.CASCADE, related_name="employees", 
    )

    @property
    def full_name(self):
        return self.name.title() + ' ' + self.surname.title()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_barbershopemployee_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('berberim_barbershopemployee_update', args=(self.pk,))


#Expand this array by customer demand
SERVICE_NAME_CHOICES = [
    ('Haircut', _('Haircut')),
    ('Beardcut', _('Beardcut')),
    ('Hair Wash', _('Hair Wash')),
]

class BarbershopServices(models.Model):

    # Fields
    name = models.CharField(max_length=30, primary_key=True, choices=SERVICE_NAME_CHOICES)
    price = models.PositiveIntegerField()
    duration_mins = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Relationship Fields
    barbershop = models.ForeignKey(
        'berberim.Barbershop',
        on_delete=models.CASCADE, related_name="services", 
    )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_barbershopservices_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('berberim_barbershopservices_update', args=(self.pk,))

        
class Address(models.Model):

    # Fields
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)

    # Relationship Fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="addressess", 
    )

    class Meta:
        ordering = ('-pk',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_addresses_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('berberim_addresses_update', args=(self.pk,))


class BarbershopSchedule(models.Model):

    # Fields
    id = models.AutoField(primary_key=True)
    services = ArrayField(
        models.CharField(max_length=32, blank=True, choices=SERVICE_NAME_CHOICES),
        default=list,
        blank=False,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    # Relationship Fields
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name="barbershopschedules", 
    )
    barbershop = models.ForeignKey(
        'berberim.Barbershop',
        on_delete=models.CASCADE, related_name="schedules", 
    )
    assigned_employee = models.ForeignKey(
        'berberim.BarbershopEmployee',
        on_delete=models.CASCADE, related_name="schedules", 
    )

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('berberim_barbershopschedule_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('berberim_barbershopschedule_update', args=(self.pk,))
