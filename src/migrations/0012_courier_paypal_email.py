# Generated by Django 3.2.5 on 2021-07-29 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0011_auto_20210721_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='courier',
            name='paypal_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
    ]