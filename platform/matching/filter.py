from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate


def filter_function(request):
    """
    Add filtering function view
    """
    if request.method == 'POST':
        
        # Get filter parameters
        destination = request.POST.get('destination')
        age = request.POST.get('age')
        exchange_school = request.POST.get('exchange_school')
        gender = request.POST.get('gender')

        # Build filter conditions
        filter_params = {}
        if destination:
            filter_params['destination'] = destination
        if age:
            filter_params['age'] = age
        if exchange_school:
            filter_params['exchange_school'] = exchange_school
        if gender:
            filter_params['gender'] = gender
        
        if 'reset' in request.POST:
            # Clear filter parameters
            filter_params = {}

        # Get the current user's profile
        current_user_profile = UserProfile.objects.get(user=request.user)
        
        # Query users based on filter parameters
        filtered_profiles = UserProfile.objects.exclude(user=request.user).filter(**filter_params)

        # Render the matching page and pass the filtered data and current user's profile
        return render(request, 'matching.html', {
            'profiles': filtered_profiles,
            'current_user_profile': current_user_profile
        })

    else:
        # If it's a GET request, directly return the matching page
        return render(request, 'matching.html')


def show_all_profiles(request):
    current_user_profile = UserProfile.objects.get(user=request.user)
    profiles = UserProfile.objects.exclude(user=request.user)
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile
    })
