# Generated by Django 2.2.7 on 2019-11-26 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('berberim', '0016_barbershopimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='barbershopimage',
            name='barbershop',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='berberim.Barbershop'),
        ),
    ]
