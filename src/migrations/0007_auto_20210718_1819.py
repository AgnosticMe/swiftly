# Generated by Django 3.2.5 on 2021-07-18 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0006_auto_20210718_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='delivery_address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='job',
            name='delivery_latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='job',
            name='delivery_longitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='job',
            name='delivery_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='job',
            name='delivery_phone',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
