from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.conf import settings

from src.models import *

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

@login_required(login_url='/sign-in/?next=/courier/')
def available_job_details_page(request,id):
    job = Job.objects.filter(id=id, status=Job.PROCESSING_STATUS).last()

    if not job:
        return redirect(reverse('courier:available_jobs'))

    if request.method == 'POST':
        job.courier = request.user.courier
        job.status = Job.PICKING_STATUS
        job.save()

        return redirect(reverse('courier:available_jobs'))
    
    context = {
        'job': job,
    }
    return render(request, 'courier/available_job_details.html', context)


@login_required(login_url='/sign-in/?next=/courier/')
def current_job_page(request):
    job = Job.objects.filter(
        courier=request.user.courier, 
        status__in=[
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS
        ]
    ).last()
    
    context = {
        "job": job,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
    }
    return render(request, 'courier/current_job.html',context)


@login_required(login_url='/sign-in/?next=/courier/')
def current_job_take_photo_page(request, id):
    job = Job.objects.filter(
        id = id, 
        courier= request.user.courier,
        status__in=[
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS,
        ]
    ).last()

    if not job:
        return redirect(reverse('courier:current_job'))

    context = {
        "job": job,
    }
    return render(request, 'courier/current_job_take_photo.html', context)


@login_required(login_url='/sign-in/?next=/courier/')
def job_complete_page(request):
    return  render(request, 'courier/job_complete.html')


@login_required(login_url='/sign-in/?next=/courier/')
def archived_jobs_page(request):
    jobs = Job.objects.filter(
        courier = request.user.courier,
        status = Job.COMPLETED_STATUS,
    )

    context = {
        'jobs': jobs,
    }
    return render(request, 'courier/archived_jobs.html', context)


@login_required(login_url='/sign-in/?next=/courier/')
def profile_page(request):
    jobs = Job.objects.filter(
        courier = request.user.courier,
        status = Job.COMPLETED_STATUS,
    )

    total_earnings = round(sum(job.price for job in jobs) * 0.8, 2)
    total_jobs = len(jobs)
    total_kms = round(sum(job.distance for job in jobs), 2)

    context = {
        'total_earnings': total_earnings,
        'total_jobs': total_jobs,
        'total_kms': total_kms,
    }

    return render(request, 'courier/profile.html', context)