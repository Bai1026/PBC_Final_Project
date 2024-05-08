from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate


def matching_list(request):
    # Retrieve the current user's profile
    current_user_profile = UserProfile.objects.get(user=request.user)

    # Fetch the list of friends (users that are already matched)
    friends = []

    # Fetch the list of matching requests received by the current user
    matching_requests_received = []

    return render(request, 'matching.html', {
        'friends': friends,
        'matching_requests_received': matching_requests_received,
        'current_user_profile': current_user_profile
    })