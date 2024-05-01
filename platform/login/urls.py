from django.urls import path
from django.conf.urls import handler403, handler404
from .views import user_login, welcome, register, user_matching, hide_profile, UserProfileUpdate

urlpatterns = [
    # path('login/', user_login, name='login'),
    path('', user_login, name='login'),
    path('welcome/', welcome, name='welcome'),
    path('register/', register, name='register'),
    path('profile/update/', UserProfileUpdate.as_view(), name='update_profile'),
    path('<str:username>/matching/', user_matching, name='user_matching'),

    path('hide-profile/<str:username>/', hide_profile, name='hide_profile'),
]

handler403 = 'login.views.custom_403'
handler404 = 'login.views.custom_404'