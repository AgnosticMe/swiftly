from re import T
from django import forms
from django.contrib.auth.models import User

from src.models import Customer, Job

class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class BasicCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('avatar', )


class JobCreateStep1Form(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('job_name', 'description', 'category', 'size', 'quantity', 'photo')


class JobCreateStep2Form(forms.ModelForm):
    pickup_address = forms.CharField(required=True)
    pickup_name = forms.CharField(required=True)
    pickup_phone = forms.CharField(required=True)

    class Meta:
        model = Job
        fields = ('pickup_address', 'pickup_latitude', 'pickup_longitude', 'pickup_name', 'pickup_phone')


