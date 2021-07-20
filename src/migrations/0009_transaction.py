# Generated by Django 3.2.5 on 2021-07-20 06:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('src', '0008_auto_20210720_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_payment_intent_id', models.CharField(max_length=255, unique=True)),
                ('amount', models.FloatField(default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='src.job')),
            ],
        ),
    ]
