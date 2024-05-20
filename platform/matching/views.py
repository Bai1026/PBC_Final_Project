from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile, DeletedProfile, MatchInvitation, Friend
from login.views import UserProfileUpdate

from .delete import delete_profile
from .hide import hide_profile
from .matching_list import matching_list
from .filter import filter_function, show_all_profiles


@login_required
def send_match_request(request, username):
    receiver = get_object_or_404(User, username=username)
    current_user_profile = UserProfile.objects.get(user=request.user)

    # 检查是否已存在从接收者到发送者的匹配请求
    existing_invitation = MatchInvitation.objects.filter(sender=receiver, receiver=request.user, mutual=False).first()
    if existing_invitation:
        # 如果存在，标记为互相匹配
        existing_invitation.mutual = True
        existing_invitation.save()
        # 创建当前用户到接收者的匹配请求，并标记为互相匹配
        MatchInvitation.objects.create(sender=request.user, receiver=receiver, mutual=True)
        # 创建朋友关系
        Friend.objects.create(user1=request.user, user2=receiver)
        messages.success(request, "You are now friends!")
    else:
        # 如果不存在，创建新的匹配请求
        MatchInvitation.objects.create(sender=request.user, receiver=receiver, mutual=False)
        messages.info(request, "Match request sent!")
    return redirect('user_matching', username=request.user.username)

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

    # 查找已被刪除的用戶
    deleted_profiles = DeletedProfile.objects.filter(user=user).values_list('deleted_user__id', flat=True)

    sent_match_requests = MatchInvitation.objects.filter(sender=user).values_list('receiver__id', flat=True)

    # 篩選掉被當前用戶隱藏的用戶和自己
    # profiles = UserProfile.objects.exclude(user__in=hidden_profiles).exclude(user__in=deleted_profiles).exclude(user=user)
    profiles = UserProfile.objects.exclude(user__in=deleted_profiles).exclude(user__in=sent_match_requests).exclude(user=user)

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

    # 獲取當前用戶的 profile 信息
    current_user_profile = UserProfile.objects.get(user=user)

    # 获取朋友列表
    friends = current_user_profile.friends

    # 返回匹配頁面
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile,
        'friends': friends,
    })