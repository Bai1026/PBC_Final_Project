from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate


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
