from django.db import models
from django.urls import reverse_lazy
from django.contrib import messages

from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone


from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.models import UserProfile, HiddenProfile

# Create your views here.
@login_required
def welcome(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return render(request, 'errors/403.html', status=403)
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    context = {
        'username': user.username,
        'profile': profile,
    }
    return render(request, 'login/welcome.html', context)