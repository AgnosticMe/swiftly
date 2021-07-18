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