from django.urls import path
from django.conf.urls import handler403, handler404

# from .views import user_login, welcome, register, user_matching, hide_profile, UserProfileUpdate, filter_function, show_all_profiles, matching_list
from .views import welcome
from login.views import UserProfileUpdate


urlpatterns = [
    path('profile_update/<str:username>/', UserProfileUpdate.as_view(), name='update_profile'),
    path('<str:username>/', welcome, name='welcome'),
]