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
        # If the UserProfile object does not exist, or the current user does not have a valid username, handle appropriately
        return render(request, '403.html')
    except User.DoesNotExist:
        # If the current user object does not exist, handle appropriately
        return render(request, '404.html')
    
    # Get the current user's friends
    friends = current_user_profile.friends

    # Return the friends.html template, passing the list of friends and the current username
    return render(request, 'friends.html', {
        'friends': friends,
        'current_user_profile': current_user_profile,
    })