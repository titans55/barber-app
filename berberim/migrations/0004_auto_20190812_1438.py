# Generated by Django 2.1.5 on 2019-08-12 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('berberim', '0003_auto_20190812_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='district',
            name='id',
        ),
        migrations.AddField(
            model_name='district',
            name='district_code',
            field=models.CharField(default=None, max_length=20, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]
