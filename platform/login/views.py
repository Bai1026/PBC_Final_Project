from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .models import UserProfile


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('welcome')
        else:
            # Check if user exists
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

# @login_required
# def matching(request):
#     # Assuming you have a UserProfile model where user profiles are stored
#     profiles = UserProfile.objects.all()  # Fetch all profiles from the database
#     return render(request, 'matching.html', {'profiles': profiles})

from django.shortcuts import render, get_object_or_404

@login_required
def user_matching(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        return render(request, 'errors/403.html', status=403)

    profiles = UserProfile.objects.all().exclude(user=user)
    current_user_profile = UserProfile.objects.get(user=user)
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile
    })



from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .forms import UserProfileForm

class UserProfileUpdate(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    
    # change to register web to update the profile
    template_name = 'login/register.html'
    success_url = reverse_lazy('welcome')

    def get_object(self, queryset=None):
        return self.request.user.userprofile


def custom_403(request, exception):
    return render(request, '403.html', {}, status=403)

def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)