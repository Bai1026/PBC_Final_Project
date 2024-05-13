from django.urls import path
from django.conf.urls import handler403, handler404

# from .views import user_login, welcome, register, user_matching, hide_profile, UserProfileUpdate, filter_function, show_all_profiles, matching_list
from .views import user_matching, hide_profile,  delete_profile, filter_function, show_all_profiles, matching_list
from login.views import UserProfileUpdate

urlpatterns = [
    # path('matching/<str:username>/', user_matching, name='user_matching'),
    path('<str:username>/', user_matching, name='user_matching'),
    path('hide-profile/<str:username>/', hide_profile, name='hide_profile'),
    path('delete/<username>/', delete_profile, name='delete_profile'),
    path('filter/', filter_function, name='filter_function'),
    path('show-all-profiles/', show_all_profiles, name='show_all_profiles'),
    path('matching-list/', matching_list, name='matching_list'),

    path('profile_update/<str:username>/', UserProfileUpdate.as_view(), name='update_profile'),
]