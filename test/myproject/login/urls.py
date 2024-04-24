# from django.urls import path
# from .views import login_view

# urlpatterns = [
#     path('', login_view, name='login'),
# ]


from django.urls import path
from .views import user_login, welcome, register

urlpatterns = [
    # 你的其他URL模式
    # path('login/', user_login, name='login'),
    path('', user_login, name='login'),
    path('welcome/', welcome, name='welcome'),
    path('register/', register, name='register'),
]
