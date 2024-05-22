# friends/urls.py

from django.urls import path
from .views import friends_list
from login.views import UserProfileUpdate
from matching.filter import filter_function, show_all_profiles

app_name = 'friends'

urlpatterns = [
    path('filter/', filter_function, name='filter_function'),
    path('show-all-profiles/', show_all_profiles, name='show_all_profiles'),
    path('profile_update/<str:username>/', UserProfileUpdate.as_view(), name='update_profile'),
    path('', friends_list, name='friends_list'),
    # 其他 friends 應用程序的 URL 配置...
]