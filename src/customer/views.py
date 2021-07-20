from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template import context
from django.urls import reverse
from src.customer import forms

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.conf import settings

import firebase_admin
from firebase_admin import credentials, auth

import stripe

from src.models import *

import requests

# Firebase Configuration
cred = credentials.Certificate({
    "type": settings.FIREBASE_TYPE,
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY,
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": settings.FIREBASE_AUTH_URI,
    "token_uri": settings.FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
})
firebase_admin.initialize_app(cred)

# stripe setup
stripe.api_key = settings.STRIPE_API_SECRET_KEY

# write your views here

@login_required()
def home(request):
    return redirect(reverse('customer:profile'))

@login_required(login_url='/sign-in/?next=/customer/')
def profile_page(request):
    user_form = forms.BasicUserForm(instance=request.user)
    customer_form = forms.BasicCustomerForm(instance=request.user.customer)
    change_password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':

        if request.POST.get('action') == 'update_profile':
            user_form = forms.BasicUserForm(request.POST, instance=request.user)
            customer_form = forms.BasicCustomerForm(request.POST,request.FILES, instance=request.user.customer)
            if user_form.is_valid() and customer_form.is_valid():
                user_form.save()
                customer_form.save()

                messages.success(request, 'Your Profile has been updated successfully!')
                return redirect(reverse('customer:profile'))

        elif request.POST.get('action') == 'update_password':
            change_password_form = PasswordChangeForm(request.user, request.POST)
            if change_password_form.is_valid():
                user = change_password_form.save()
                update_session_auth_hash(request, user)

                messages.success(request, 'Your Password has been updated successfully!')
                return redirect(reverse('customer:profile'))

        elif request.POST.get('action') == 'update_phone':
            # Get Firebase user data
            firebase_user = auth.verify_id_token(request.POST.get('id_token'))

            request.user.customer.phone_number = firebase_user['phone_number']
            request.user.customer.save()
            return redirect(reverse('customer:profile'))

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'change_password_form': change_password_form,

        # firebase configuration
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
    }
    return render(request, 'customer/profile.html', context)


@login_required(login_url='/sign-in/?next=/customer/')
def payment_method_page(request):
    current_customer = request.user.customer

    # remove existing card
    if request.method == 'POST':
        stripe.PaymentMethod.detach(current_customer.stripe_payment_method_id)
        current_customer.stripe_payment_method_id = ""
        current_customer.stripe_card_last4 = ""
        current_customer.save()
        return redirect(reverse('customer:payment_method'))

    # save stripe customer info
    if not current_customer.stripe_customer_id:
        customer = stripe.Customer.create()
        current_customer.stripe_customer_id = customer['id']
        current_customer.save()

    # Get stripe payment method of the customer
    stripe_payment_methods = stripe.PaymentMethod.list(customer=current_customer.stripe_customer_id, type="card")

    if stripe_payment_methods and len(stripe_payment_methods.data) > 0:
        payment_method = stripe_payment_methods.data[0]
        current_customer.stripe_payment_method_id = payment_method.id
        current_customer.stripe_card_last4 = payment_method.card.last4
        current_customer.save()
    else:
        current_customer.stripe_payment_method_id = ""
        current_customer.stripe_card_last4 = ""
        current_customer.save()

    if not current_customer.stripe_payment_method_id:
        intent = stripe.SetupIntent.create(customer = current_customer.stripe_customer_id)
        context = {
            "client_secret": intent.client_secret,
            "STRIPE_API_PUBLIC_KEY": settings.STRIPE_API_PUBLIC_KEY,
        }
        return render(request, 'customer/payment_method.html', context)
    else:
        return render(request, 'customer/payment_method.html')


@login_required(login_url='/sign-in/?next=/customer/')
def create_job_page(request):
    current_customer = request.user.customer
    if not current_customer.stripe_payment_method_id:
        return redirect(reverse('customer:payment_method'))
    
    has_current_job = Job.objects.filter(
        customer=current_customer,
        status__in=[
            Job.PROCESSING_STATUS,
            Job.PICKING_STATUS,
            Job.DELIVERING_STATUS,
        ]
    ).exists()

    if has_current_job:
        messages.warning(request, "You currently have an active job.")
        return redirect(reverse('customer:current_jobs'))

    creating_job = Job.objects.filter(customer=current_customer, status=Job.CREATING_STATUS).last()
    step1_form = forms.JobCreateStep1Form(instance=creating_job)
    step2_form = forms.JobCreateStep2Form(instance=creating_job)
    step3_form = forms.JobCreateStep3Form(instance=creating_job)

    if request.method == 'POST':
        if request.POST.get('step') == '1':
            step1_form = forms.JobCreateStep1Form(request.POST, request.FILES, instance=creating_job)
            if step1_form.is_valid():
                creating_job = step1_form.save(commit=False)
                creating_job.customer = current_customer
                creating_job.save()
                return redirect(reverse('customer:create_job'))

        elif request.POST.get('step') == '2':
            step2_form = forms.JobCreateStep2Form(request.POST, instance=creating_job)
            if step2_form.is_valid():
                creating_job = step2_form.save()
                return redirect(reverse('customer:create_job'))
            
        elif request.POST.get('step') == '3':
            step3_form = forms.JobCreateStep3Form(request.POST, instance=creating_job)
            if step3_form.is_valid():
                creating_job = step3_form.save()
                try:
                    r = requests.get(f"https://maps.google.com/maps/api/distancematrix/json?origins={creating_job.pickup_address}&destinations={creating_job.delivery_address}&mode=transit&key={settings.GOOGLE_API_KEY}")

                    distance = r.json()['rows'][0]['elements'][0]['distance']['value']
                    duration = r.json()['rows'][0]['elements'][0]['duration']['value']
                    creating_job.distance = round(distance / 1000, 2)
                    creating_job.duration = round(duration / 60)
                    creating_job.price = round(creating_job.distance * 7, 2)  # ₹7 per km
                    creating_job.save()

                except Exception as e:
                    print(e)
                    messages.error(request, "Unfortunately, we do not support shipping at this distance")

                return redirect(reverse('customer:create_job'))

        elif request.POST.get('step') == '4':
            if creating_job.price:
                try:
                    payment_intent = stripe.PaymentIntent.create(
                        amount=int(creating_job.price * 100),
                        currency='inr',
                        customer=current_customer.stripe_customer_id,
                        payment_method=current_customer.stripe_payment_method_id,
                        off_session=True,
                        confirm=True,
                    )

                    Transaction.objects.create(
                        stripe_payment_intent_id = payment_intent['id'],
                        job = creating_job,
                        amount = creating_job.price,
                    )

                    creating_job.status = Job.PROCESSING_STATUS
                    creating_job.save()

                    return redirect(reverse('customer:home'))

                except stripe.error.CardError as e:
                    err = e.error
                    # Error code will be authentication_required if authentication is needed
                    print("Code is: %s" % err.code)
                    payment_intent_id = err.payment_intent['id']
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    # Determine the current step
    if not creating_job:
        current_step = 1
    elif creating_job.delivery_name:
        current_step = 4
    elif creating_job.pickup_name:
        current_step = 3
    else:
        current_step = 2

    context = {
        'job': creating_job,
        'step' : current_step,
        'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        'step1_form': step1_form,
        'step2_form': step2_form,
        'step3_form': step3_form,
    }
    return render(request, 'customer/create_job.html', context)

@login_required(login_url='/sign-in/?next=/customer/')
def current_jobs_page(request):
    jobs = Job.objects.filter(
        customer = request.user.customer, 
        status__in=[
            Job.PROCESSING_STATUS, 
            Job.PICKING_STATUS, 
            Job.DELIVERING_STATUS
        ]
    )

    context = {
        "jobs": jobs,
    }
    return render(request, 'customer/jobs.html', context)


@login_required(login_url='/sign-in/?next=/customer/')
def archived_jobs_page(request):
    jobs = Job.objects.filter(
        customer = request.user.customer, 
        status__in=[
            Job.COMPLETED_STATUS, 
            Job.CANCELLED_STATUS, 
        ]
    )

    context = {
        "jobs": jobs,
    }
    return render(request, 'customer/jobs.html', context)

@login_required(login_url='/sign-in/?next=/customer/')
def job_details_page(request, job_id):
    job = Job.objects.get(id=job_id)

    if request.method == 'POST' and job.status ==Job.PROCESSING_STATUS:
        job.status = Job.CANCELLED_STATUS
        job.save()
        return redirect(reverse('customer:archived_jobs'))


    context = {
        'job': job,
        "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
    }
    return render(request, 'customer/job_details.html', context)

