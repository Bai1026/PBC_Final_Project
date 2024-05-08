# matching/profile_operations.py

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from login.models import User, UserProfile

# Max part
@login_required
def delete_profile(request, username):
    """
    永久刪除指定用戶的 profile。
    """
    # 根據用戶名查找要刪除的目標用戶
    user_to_delete = get_object_or_404(User, username=username)
    user_profile_to_delete = UserProfile.objects.get(user=user_to_delete)

    # 檢查是否已經存在隱藏/刪除記錄
    # hidden_profile, created = HiddenProfile.objects.get_or_create(user=request.user, hidden_user=user_profile_to_delete)
    # hidden_profile.is_deleted = True  # 標記為完全刪除
    # hidden_profile.save()

    # 嘗試獲取對應的 UserProfile，如果存在則一併刪除
    try:
        user_profile_to_delete = UserProfile.objects.get(user=user_to_delete)
        user_profile_to_delete.delete()
    except UserProfile.DoesNotExist:
        pass

    # 永久刪除該用戶
    user_to_delete.delete()


    messages.success(request, "User profile has been deleted successfully.")
    return redirect('user_matching', username=request.user.username)
