# Generated by Django 2.2.7 on 2020-01-31 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('berberim', '0019_auto_20200131_2243'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='name_en',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='name_tr',
            field=models.CharField(max_length=30, null=True),
        ),
    ]