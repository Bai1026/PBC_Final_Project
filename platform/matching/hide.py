from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import User, UserProfile
from login.models import UserProfile, HiddenProfile

@login_required
def hide_profile(request, username):
    """
    隱藏指定用戶的 profile，不再在匹配列表中顯示。
    """
    # 根據用戶名查找目標用戶
    user_to_hide = get_object_or_404(User, username=username)
    user_profile_to_hide = UserProfile.objects.get(user=user_to_hide)

    # Check if the profile has already been hidden by this user
    hidden_profile, created = HiddenProfile.objects.get_or_create(user=request.user, hidden_user=user_profile_to_hide)
    
    # 更新隱藏次數或創建新的隱藏記錄
    if not created:
        hidden_profile.hide_count += 1  # Increment the hide count
        hidden_profile.save()
        messages.success(request, "Hide count incremented.")
    else:
        messages.success(request, "Profile successfully hidden for the first time.")

    # 返回匹配頁面
    return redirect('user_matching', username=request.user.username)