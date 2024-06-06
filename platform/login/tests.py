# login/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# whenever change the models.py, we should make the migration and migrate
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nation = models.CharField(max_length=100, blank=True, null=True)
    destination = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    exchange_school = models.CharField(max_length=100, blank=True, null=True)
    # date = models.DateField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female'),('O','Others')), blank=True, null=True)

    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    other_social_media = models.CharField(max_length=100, blank=True, null=True)
    avatar1 = models.ImageField(upload_to='avatars', blank=True, null=True)
    avatar2 = models.ImageField(upload_to='avatars', blank=True, null=True)
    avatar3 = models.ImageField(upload_to='avatars', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    @property
    def friends(self):
        friends1 = self.user.friends1.all()
        friends2 = self.user.friends2.all()
        return list(friends1) + list(friends2)


class RecommendationScore(models.Model):
    user_from = models.ForeignKey(User, related_name='recommendations_given', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='recommendations_received', on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        unique_together = ('user_from', 'user_to')


class HiddenProfile(models.Model):
    user = models.ForeignKey(User, related_name='hiding_user', on_delete=models.CASCADE)
    hidden_user = models.ForeignKey(UserProfile, related_name='hidden_profile', on_delete=models.CASCADE)
    hide_count = models.IntegerField(default=1)  # Tracks how often a profile has been hidden

    class Meta:
        unique_together = ('user', 'hidden_user')  # Ensures uniqueness


class DeletedProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deleted_profiles')
    deleted_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='deleted_profile')

    class Meta:
        unique_together = ('user', 'deleted_user')  # Ensures uniqueness


class MatchInvitation(models.Model):
    sender = models.ForeignKey(User, related_name='sent_invitations', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_invitations', on_delete=models.CASCADE)
    # status = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('accepted', 'Accepted')], default='sent')
    mutual = models.BooleanField(default=False)


class Friend(models.Model):
    user1 = models.ForeignKey(User, related_name='friends1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friends2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Ensures the uniqueness of the friendship relationship

    def __str__(self):
        # return f"{self.user1.username} and {self.user2.username} are friends"
        return f"{self.user1.username} & {self.user2.username}"
    
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


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
