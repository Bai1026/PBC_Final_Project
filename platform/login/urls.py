from django.urls import path
from django.conf.urls import handler403, handler404
from .views import user_login, register, UserProfileUpdate


urlpatterns = [
    path('', user_login, name='login'),
    path('register/', register, name='register'),
    path('profile/update/<str:username>/', UserProfileUpdate.as_view(), name='update_profile'),
]