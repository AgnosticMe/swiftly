# Generated by Django 3.2.5 on 2021-07-29 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0013_transaction_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='fcm_token',
            field=models.TextField(blank=True),
        ),
    ]
