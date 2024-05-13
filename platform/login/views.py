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
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, HiddenProfile


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Clear hidden profiles before logging in
            HiddenProfile.objects.filter(user=user).delete()
            login(request, user)
            # return redirect('welcome')
            return redirect('welcome', username=user.username)

        else:
            if User.objects.filter(username=username).exists():
                error_message = "Password is incorrect."
            else:
                error_message = "Account doesn't exist."
            return render(request, 'login/login.html', {'error': error_message})
    else:
        return render(request, 'login/login.html')


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()

            # Create or update the user profile
            profile_form = UserProfileForm(request.POST, request.FILES, instance=new_user.userprofile)
            if profile_form.is_valid():
                profile_form.save()
                
            # after register, login the account automatically.
            login(request, new_user)

            # redirect to welcome page
            # return redirect('welcome')
            return redirect('welcome', username=new_user.username)

    else:
        form = UserRegistrationForm()
    return render(request, 'login/register.html', {'form': form})

# class UserProfileUpdate(UpdateView):
#     model = UserProfile
#     form_class = UserProfileForm
#     template_name = 'login/register.html'
#     success_url = reverse_lazy('welcome')  # You might need to adjust this

#     def get_object(self, queryset=None):
#         username = self.kwargs.get('username')
#         user = get_object_or_404(User, username=username)
#         if self.request.user != user:
#             # Optionally raise a permission denied
#             raise PermissionDenied
#         return self.request.user.userprofile

class UserProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'login/register.html'

    def get_success_url(self):
        return reverse_lazy('user_matching', kwargs={'username': self.kwargs['username']})

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        if self.request.user != user:
            raise PermissionDenied
        return self.request.user.userprofile
