from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import OuterRef, Subquery, Sum, Case, When, IntegerField, FloatField, F
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile, DeletedProfile, MatchInvitation, Friend, RecommendationScore
from login.views import UserProfileUpdate

from .delete import delete_profile
from .hide import hide_profile
from .matching_list import matching_list
from .filter import filter_function, show_all_profiles

import pandas as pd
from sklearn.neighbors import NearestNeighbors
import os
os.environ['LOKY_MAX_CPU_COUNT'] = '4'  # 设置使用4个核心

@login_required
def recommend_scores(current_user_profile):
    # profiles = list(UserProfile.objects.exclude(user=current_user_profile.user).values())
    profiles = list(UserProfile.objects.all().values())  # 獲取所有用戶，包括當前用戶
    df = pd.DataFrame(profiles)

    # 确保必需列存在
    required_columns = ['destination']
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna(-999)  # 直接赋值以避免警告
        # 使用负值填充缺失的 'destination' 列


    df = pd.get_dummies(df, columns=['destination'])

    if 'age' not in df.columns:
        # df['age'] = 0
        df['age'] = -999  # 使用一个极端的负值作为默认值，使其在排序中较低
    else:
        df['age'] = df['age'].fillna(-999).astype(int)  # 确保 age 列中的值都是整数，并用负值填充缺失值

    # df['age'] = df['age'].fillna(0).astype(int)  # 確保 age 列中的值都是整數
    
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0).infer_objects()

    # print("DataFrame after preprocessing:\n", df.head())

    if df.empty:
        return {}

    current_user_age = current_user_profile.age if current_user_profile.age is not None else 0

    # age_distances = []
    # for profile in profiles:
    #     age = profile.get('age', 0)
    #     if age is None:
    #         age = 0
    #     age_distance = abs(current_user_age - int(age))  # 確保 age 是整數
    #     age_distances.append(age_distance)
    
    # 计算年龄差异
    age_distances = []
    for profile in profiles:
        age = profile.get('age', -999)
        if age is None:
            age = -999
        age_distance = abs(current_user_age - age)  # 确保 age 是整数
        age_distances.append(age_distance)

    features_for_knn = [col for col in df.columns if col not in ['id', 'user_id', 'age']]
    # if not features_for_knn:
    #     print("Error: No features available for KNN")
    #     return {}

    df_features = df[features_for_knn]

    model = NearestNeighbors(n_neighbors=len(profiles)).fit(df_features)
    distances, indices = model.kneighbors(df_features)

    # print("Distances:\n", distances)
    # print("Indices:\n", indices)

    # # 调试信息：检查当前用户的 user_id
    # print("Current user ID:", current_user_profile.user.id)
    # print("Profiles user IDs:", [profile['user_id'] for profile in profiles])
    
    # 調試：檢查當前用戶的 ID 是否在資料框中
    current_user_id = current_user_profile.user.id
    user_ids = [profile['user_id'] for profile in profiles]
    # if current_user_id not in user_ids:
    #     print(f"Error: Current user ID {current_user_id} not found in profiles")
    #     return {}

    user_idx = next((idx for idx, profile in enumerate(profiles) if profile['user_id'] == current_user_id), None)

    # if user_idx is None:
    #     print(f"Error: current_user_profile user ID {current_user_id} not found in profiles")
    #     return {}
    
    scores = {}
    for j, i in enumerate(indices[user_idx]):
        if i != user_idx:
            distance_score = max(0, 100 - min(distances[user_idx][j], 100))
            age_score = max(0, 100 - min(age_distances[i], 100)) if age_distances[i] != 0 else distance_score
            combined_score = 0.7 * distance_score + 0.3 * age_score
            scores[profiles[i]['user_id']] = combined_score
            
            # 更新推荐分数到 RecommendationScore 模型
            recommendation_score, created = RecommendationScore.objects.update_or_create(
                user_from=current_user_profile.user,
                user_to_id=profiles[i]['user_id'],
                defaults={'score': combined_score}
            )
            # print(f"Updated score for user {profiles[i]['user_id']}: {recommendation_score.score}")

    # print("Scores:\n", scores)

    return scores


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

    # 獲取當前用戶的 profile 信息
    current_user_profile = UserProfile.objects.get(user=user)
    # Fetch profiles not hidden by the current user
    hidden_profiles = HiddenProfile.objects.filter(user=user).values_list('hidden_user__id', flat=True)
    # 查找已被刪除的用戶
    deleted_profiles = DeletedProfile.objects.filter(user=user).values_list('deleted_user__id', flat=True)

    sent_match_requests = MatchInvitation.objects.filter(sender=user).values_list('receiver__id', flat=True)
    # 篩選掉被當前用戶隱藏的用戶和自己
    profiles = UserProfile.objects.exclude(user__in=deleted_profiles).exclude(user__in=sent_match_requests).exclude(user=user)

    # 獲取推薦分數
    recommendation_scores = recommend_scores(current_user_profile)

    # # 確保推薦分數已成功計算和存儲
    # for user_id, score in recommendation_scores.items():
    #     print(f"User {user_id} recommendation score: {score}")
    #     # 檢查RecommendationScore是否正確存儲
    #     recommendation_score = RecommendationScore.objects.filter(user_from=current_user_profile.user, user_to_id=user_id).first()
    #     if recommendation_score:
    #         print(f"Database stored score for user {user_id}: {recommendation_score.score}")

    # Order profiles by the number of times they have been hidden
    profiles = profiles.annotate(
        total_hide_count=Sum(
            Case(
                When(hidden_profile__in=HiddenProfile.objects.filter(hidden_user=OuterRef('pk')), then='hidden_profile__hide_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        # 排序部分
        annotated_recommendation_score=Subquery(
            RecommendationScore.objects.filter(
                user_from=current_user_profile.user,
                user_to=OuterRef('user')
            ).values('score')[:1],
            output_field=FloatField()
        )
    ).order_by('-annotated_recommendation_score', 'total_hide_count')
    # ).order_by('total_hide_count')


    # # 打印profiles中的recommendation_score以進行調試
    # for profile in profiles:
    #     print(profile.user.username, profile.annotated_recommendation_score)

    # 获取朋友列表
    friends = current_user_profile.friends

    # 返回匹配頁面
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile,
        'friends': friends,
    })