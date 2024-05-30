# matching/profile_operations.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import User, UserProfile
from login.models import DeletedProfile

# Max part
@login_required
def delete_profile(request, username):
    """
    Permanently delete the profile of the specified user.
    """
    # Find the target user to be deleted by username
    user_to_delete = get_object_or_404(User, username=username)
    user_profile_to_delete = UserProfile.objects.get(user=user_to_delete)

    # Check if a deletion record already exists
    deleted_profile, created = DeletedProfile.objects.get_or_create(user=request.user, deleted_user=user_profile_to_delete)

    if not created:
        messages.info(request, f"{username} is already deleted.")
    else:
        messages.success(request, f"User {username} has been permanently removed from your interface.")

    # Return to the matching page
    return redirect('user_matching', username=request.user.username)
