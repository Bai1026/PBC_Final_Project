from django.urls import path
from django.conf.urls import handler403, handler404
<<<<<<< HEAD
# from .views import user_login, welcome, register, user_matching, hide_profile, UserProfileUpdate, filter_function, show_all_profiles, matching_list
=======
# from .views import user_login, welcome, register, user_matching, hide_profile, UserProfileUpdate, filter_function, show_all_profiles, matching_list
from .views import user_login, welcome, register, user_matching, hide_profile,  delete_profile, UserProfileUpdate, filter_function, show_all_profiles, matching_list
>>>>>>> 86768c7 (WIP: Save local changes before merging)

urlpatterns = [
    # path('login/', user_login, name='login'),
    path('', user_login, name='login'),
    path('welcome/', welcome, name='welcome'),
    path('register/', register, name='register'),
    path('profile/update/', UserProfileUpdate.as_view(), name='update_profile'),

    # Max part
    # path('<str:username>/matching/', user_matching, name='user_matching'), 
    path('matching/<str:username>/', user_matching, name='user_matching'),  # 添加此路由

    path('hide-profile/<str:username>/', hide_profile, name='hide_profile'),
    # Max
    path('delete/<username>/', delete_profile, name='delete_profile'),

    # 篩選路徑
    path('filter/', filter_function, name='filter_function'),
    path('show-all-profiles/', show_all_profiles, name='show_all_profiles'),
    path('matching-list/', matching_list, name='matching_list')
]

handler403 = 'login.views.custom_403'
handler404 = 'login.views.custom_404'