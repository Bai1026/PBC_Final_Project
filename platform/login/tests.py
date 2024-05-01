from django.test import TestCase

from django.db import models
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, HiddenProfile


def custom_403(request, exception):
    return render(request, '403.html', {}, status=403)


def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Clear hidden profiles before logging in
            HiddenProfile.objects.filter(user=user).delete()
            login(request, user)
            return redirect('welcome')
        else:
            if User.objects.filter(username=username).exists():
                error_message = "Password is incorrect."
            else:
                error_message = "Account doesn't exist."
            return render(request, 'login/login.html', {'error': error_message})
    else:
        return render(request, 'login/login.html')


@login_required
def welcome(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'username': request.user.username,
        'profile': profile,
    }
    return render(request, 'login/welcome.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            # after register, login the account automatically.
            login(request, new_user)
            # redirect to welcome page
            return redirect('welcome')
    else:
        form = UserRegistrationForm()
    return render(request, 'login/register.html', {'form': form})


@login_required
def user_matching(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return render(request, 'errors/403.html', status=403)

    # Fetch profiles not hidden by the current user
    hidden_profiles = HiddenProfile.objects.filter(user=user).values_list('hidden_user__id', flat=True)

    profiles = UserProfile.objects.exclude(user__in=hidden_profiles)
    # do not show the user itself
    profiles = UserProfile.objects.exclude(user=user)

    # Order profiles by the number of times they have been hidden
    profiles = profiles.annotate(
        total_hide_count=models.Sum(
            models.Case(
                models.When(hidden_profile__in=HiddenProfile.objects.filter(hidden_user=models.OuterRef('pk')), then='hidden_profile__hide_count'),
                default=0,
                output_field=models.IntegerField()
            )
        )
    ).order_by('total_hide_count')

    current_user_profile = UserProfile.objects.get(user=user)
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile
    })


@login_required
def hide_profile(request, username):
    user_to_hide = get_object_or_404(User, username=username)
    user_profile_to_hide = UserProfile.objects.get(user=user_to_hide)

    # Check if the profile has already been hidden by this user
    hidden_profile, created = HiddenProfile.objects.get_or_create(user=request.user, hidden_user=user_profile_to_hide)
    
    if not created:
        hidden_profile.hide_count += 1  # Increment the hide count
        hidden_profile.save()
        messages.success(request, "Hide count incremented.")
    else:
        messages.success(request, "Profile successfully hidden for the first time.")

    return redirect('user_matching', username=request.user.username)


class UserProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    
    # change to register web to update the profile
    template_name = 'login/register.html'
    success_url = reverse_lazy('welcome')

    def get_object(self, queryset=None):
        return self.request.user.userprofile

