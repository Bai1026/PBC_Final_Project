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
    永久刪除指定用戶的 profile。
    """
    # 根據用戶名查找要刪除的目標用戶
    user_to_delete = get_object_or_404(User, username=username)
    user_profile_to_delete = UserProfile.objects.get(user=user_to_delete)

    # 檢查是否已經存在刪除記錄
    deleted_profile, created = DeletedProfile.objects.get_or_create(user=request.user, deleted_user=user_profile_to_delete)

    if not created:
        messages.info(request, f"{username} is already deleted.")
    else:
        messages.success(request, f"User {username} has been permanently removed from your interface.")

    # 返回匹配頁面
    return redirect('user_matching', username=request.user.username)
