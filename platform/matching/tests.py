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
os.environ['LOKY_MAX_CPU_COUNT'] = '4'  # 4 cores 

@login_required
def recommend_scores(current_user_profile):
    # profiles = list(UserProfile.objects.exclude(user=current_user_profile.user).values())
    profiles = list(UserProfile.objects.all().values())  # get all users, including the users themselves
    df = pd.DataFrame(profiles)

    # Ensure required columns exist
    required_columns = ['destination']
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna(-999)  # Direct assignment to avoid warning
        # Fill missing 'destination' column with negative values

    df = pd.get_dummies(df, columns=['destination'])

    if 'age' not in df.columns:
        # df['age'] = 0
        df['age'] = -999  # Use an extreme negative value as the default
    else:
        df['age'] = df['age'].fillna(-999).astype(int) 
        # Ensure all values in the 'age' column are integers, and fill missing values with negative values
    
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0).infer_objects()

    # print("DataFrame after preprocessing:\n", df.head())

    if df.empty:
        return {}

    current_user_age = current_user_profile.age if current_user_profile.age is not None else 0
    
    # Calculate age differences
    age_distances = []
    for profile in profiles:
        age = profile.get('age', -999)
        if age is None:
            age = -999
        age_distance = abs(current_user_age - age)  # Ensure age is an integer
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

    # print("Current user ID:", current_user_profile.user.id)
    # print("Profiles user IDs:", [profile['user_id'] for profile in profiles])
    
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
            
            # update the recommodation scores
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

    # Check if there is already a match request from the receiver to the sender
    existing_invitation = MatchInvitation.objects.filter(sender=receiver, receiver=request.user, mutual=False).first()
    if existing_invitation:
        # If it exists, mark as mutually matched
        existing_invitation.mutual = True
        existing_invitation.save()
        # Create a match request from the current user to the receiver, and mark as mutually matched
        MatchInvitation.objects.create(sender=request.user, receiver=receiver, mutual=True)
        # Create a friendship
        Friend.objects.create(user1=request.user, user2=receiver)
        messages.success(request, "You are now friends!")
    else:
        # If it doesn't exist, create a new match request
        MatchInvitation.objects.create(sender=request.user, receiver=receiver, mutual=False)
        messages.info(request, "Match request sent!")
    return redirect('user_matching', username=request.user.username)

@login_required
def user_matching(request, username):
    """
    Display the matching platform page, filtering out users who have been hidden and the user themselves.
    """
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return render(request, 'errors/403.html', status=403)

    current_user_profile = UserProfile.objects.get(user=user)
    hidden_profiles = HiddenProfile.objects.filter(user=user).values_list('hidden_user__id', flat=True)
    deleted_profiles = DeletedProfile.objects.filter(user=user).values_list('deleted_user__id', flat=True)

    sent_match_requests = MatchInvitation.objects.filter(sender=user).values_list('receiver__id', flat=True)
    # Filter out users hidden by the current user and the user themselves
    profiles = UserProfile.objects.exclude(user__in=deleted_profiles).exclude(user__in=sent_match_requests).exclude(user=user)

    # Get recommendation scores
    recommendation_scores = recommend_scores(current_user_profile)

    # Order profiles by the number of times they have been hidden
    profiles = profiles.annotate(
        total_hide_count=Sum(
            Case(
                When(hidden_profile__in=HiddenProfile.objects.filter(hidden_user=OuterRef('pk')), then='hidden_profile__hide_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        # arrangement
        annotated_recommendation_score=Subquery(
            RecommendationScore.objects.filter(
                user_from=current_user_profile.user,
                user_to=OuterRef('user')
            ).values('score')[:1],
            output_field=FloatField()
        )
    ).order_by('total_hide_count', '-annotated_recommendation_score')

    # for profile in profiles:
    #     print(profile.user.username, profile.annotated_recommendation_score)

    # friend list
    friends = current_user_profile.friends

    # return to matching platform
    return render(request, 'matching.html', {
        'profiles': profiles,
        'current_user_profile': current_user_profile,
        'friends': friends,
    })

from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile
from login.views import UserProfileUpdate


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

from django.db import models
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import OuterRef, Subquery, Sum, Case, When, IntegerField, FloatField, F

from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView
from login.forms import UserRegistrationForm, UserProfileForm
from login.models import UserProfile, HiddenProfile, RecommendationScore
from login.views import UserProfileUpdate


def filter_function(request):
    """
    Add filtering function view
    """
    if request.method == 'POST':
        
        # Get filter parameters
        destination = request.POST.get('destination')
        age = request.POST.get('age')
        exchange_school = request.POST.get('exchange_school')
        gender = request.POST.get('gender')

        # Build filter conditions
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
            # Clear filter parameters
            filter_params = {}

        # Get the current user's profile
        current_user_profile = UserProfile.objects.get(user=request.user)
        
        # Query users based on filter parameters
        filtered_profiles = UserProfile.objects.exclude(user=request.user).filter(**filter_params)

        # Annotate with recommendation scores and hide counts
        filtered_profiles = filtered_profiles.annotate(
            total_hide_count=Sum(
                Case(
                    When(hidden_profile__in=HiddenProfile.objects.filter(hidden_user=OuterRef('pk')), then='hidden_profile__hide_count'),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            annotated_recommendation_score=Subquery(
                RecommendationScore.objects.filter(
                    user_from=current_user_profile.user,
                    user_to=OuterRef('user')
                ).values('score')[:1],
                output_field=FloatField()
            )
        ).order_by('total_hide_count', '-annotated_recommendation_score')


        # Render the matching page and pass the filtered data and current user's profile
        return render(request, 'matching.html', {
            'profiles': filtered_profiles,
            'current_user_profile': current_user_profile
        })

    else:
        # If it's a GET request, directly return the matching page
        return render(request, 'matching.html')

def show_all_profiles(request):
    # current_user_profile = UserProfile.objects.get(user=request.user)
    # profiles = UserProfile.objects.exclude(user=request.user)
    # return render(request, 'matching.html', {
    #     'profiles': profiles,
    #     'current_user_profile': current_user_profile
    # })
    return redirect('user_matching', username=request.user.username)


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

