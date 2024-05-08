from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate


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


# 新增筛选功能的视图函数
def filter_function(request):
    if request.method == 'POST':
        
        # 获取筛选参数
        destination = request.POST.get('destination')
        age = request.POST.get('age')
        exchange_school = request.POST.get('exchange_school')
        gender = request.POST.get('gender')

        # 构建筛选条件
        filter_params = {}
        if destination:
            filter_params['destination'] = destination
        if age:
            filter_params['age'] = age
        if exchange_school:
            filter_params['exchange_school'] = exchange_school
        if gender:
            filter_params['gender'] = gender
        
        if 'reset' in request.POST:
            # 清空筛选参数
            filter_params = {}

        # 获取当前用户的profile
        current_user_profile = UserProfile.objects.get(user=request.user)
        
        # 根据筛选参数查询用户
        filtered_profiles = UserProfile.objects.exclude(user=request.user).filter(**filter_params)

        # 渲染匹配页面，并传递筛选后的数据和当前用户的profile
        return render(request, 'matching.html', {
            'profiles': filtered_profiles,
            'current_user_profile': current_user_profile
        })

    else:
        # 如果是 GET 请求，直接返回匹配页面
        return render(request, 'matching.html')


def show_all_profiles(request):
    current_user_profile = UserProfile.objects.get(user=request.user)
    profiles = UserProfile.objects.exclude(user=request.user)
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile
    })


def matching_list(request):
    # Retrieve the current user's profile
    current_user_profile = UserProfile.objects.get(user=request.user)

    # Fetch the list of friends (users that are already matched)
    friends = []

    # Fetch the list of matching requests received by the current user
    matching_requests_received = []

    return render(request, 'matching.html', {
        'friends': friends,
        'matching_requests_received': matching_requests_received,
        'current_user_profile': current_user_profile
    })