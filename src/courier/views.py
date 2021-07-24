from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.conf import settings

# Create your views here.

@login_required(login_url='/sign-in/?next=/courier/')
def home(request):
    return redirect(reverse('courier:available_jobs'))

@login_required(login_url='/sign-in/?next=/courier/')
def available_jobs_page(request):

    context = {
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
    }
    return render(request, 'courier/available_jobs.html', context)

