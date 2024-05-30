from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import User, UserProfile
from login.models import UserProfile, HiddenProfile

@login_required
def hide_profile(request, username):
    """
    Hide the specified user's profile so it no longer appears in the matching list.
    """
    # Find the target user by username
    user_to_hide = get_object_or_404(User, username=username)
    user_profile_to_hide = UserProfile.objects.get(user=user_to_hide)

    # Check if the profile has already been hidden by this user
    hidden_profile, created = HiddenProfile.objects.get_or_create(user=request.user, hidden_user=user_profile_to_hide)
    
    # Update the hide count or create a new hidden profile record
    if not created:
        hidden_profile.hide_count += 1  # Increment the hide count
        hidden_profile.save()
        messages.success(request, "Hide count incremented.")
    else:
        messages.success(request, "Profile successfully hidden for the first time.")

    # Return to the matching page
    return redirect('user_matching', username=request.user.username)