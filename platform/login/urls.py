from django.urls import path
from .views import user_login, welcome, register, user_matching, UserProfileUpdate

urlpatterns = [
    # 你的其他URL模式
    # path('login/', user_login, name='login'),
    path('', user_login, name='login'),
    path('welcome/', welcome, name='welcome'),
    path('register/', register, name='register'),
    path('profile/update/', UserProfileUpdate.as_view(), name='update_profile'),
    path('<str:username>/matching/', user_matching, name='user_matching'),
]
