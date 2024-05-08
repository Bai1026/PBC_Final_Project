from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate

from .delete import delete_profile
from .hide import hide_profile
from .matching_list import matching_list
from .filter import filter_function, show_all_profiles


@login_required
def user_matching(request, username):
    """
    用於顯示匹配平台頁面，篩選掉已被隱藏和自己用戶的用戶。
    """
    # 確保用戶存在並驗證用戶身份
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return render(request, 'errors/403.html', status=403)

    # Fetch profiles not hidden by the current user
    hidden_profiles = HiddenProfile.objects.filter(user=user).values_list('hidden_user__id', flat=True)

    # 篩選掉被當前用戶隱藏的用戶和自己
    profiles = UserProfile.objects.exclude(user__in=hidden_profiles).exclude(user=user)

    # Order profiles by the number of times they have been hidden
    profiles = profiles.annotate(
        total_hide_count=models.Sum(
            models.Case(
                models.When(hidden_profile__in=HiddenProfile.objects.filter(hidden_user=models.OuterRef('pk')), then='hidden_profile__hide_count'),
                default=0,
                output_field=models.IntegerField()
            )
        )
    ).order_by('total_hide_count')

    # Max part
    # Fetch profiles not hidden or deleted by the current user
    excluded_profiles = HiddenProfile.objects.filter(user=user, is_deleted=True).values_list('hidden_user__id', flat=True)
    profiles = UserProfile.objects.exclude(user__in=excluded_profiles)

    # 獲取當前用戶的 profile 信息
    current_user_profile = UserProfile.objects.get(user=user)

    # 返回匹配頁面
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile
    })