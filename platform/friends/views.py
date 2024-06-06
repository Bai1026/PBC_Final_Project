from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from login.models import UserProfile
from django.contrib.auth.models import User

# Create your views here.
@login_required
def friends_list(request):
    try:
        # Get the current user's UserProfile object
        current_user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        username = current_user_profile.user.username
    except UserProfile.DoesNotExist:
        # if the current user's UserProfile object does not exist, you can take appropriate action
        return render(request, '403.html')
    except User.DoesNotExist:
        # if the current user does not exist, you can take appropriate action
        return render(request, '404.html')
    
    # Get the current user's friends list
    friends = current_user_profile.friends

    # Render the friends list page
    return render(request, 'friends.html', {
        'friends': friends,
        'current_user_profile': current_user_profile,
    })