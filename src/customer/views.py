from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from src.customer import forms

from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.

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

    context = {
        'user_form': user_form,
        'customer_form': customer_form,
        'change_password_form': change_password_form,
    }
    return render(request, 'customer/profile.html', context)
    