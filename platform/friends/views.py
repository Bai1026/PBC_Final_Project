from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from login.models import UserProfile
from django.contrib.auth.models import User

# Create your views here.
@login_required
def friends_list(request):
    try:
        # 获取当前用户的UserProfile对象
        current_user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        username = current_user_profile.user.username
    except UserProfile.DoesNotExist:
        # 如果UserProfile对象不存在，或者当前用户没有有效的用户名，可以采取适当的处理方式
        return render(request, '403.html')
    except User.DoesNotExist:
        # 如果当前用户对象不存在，可以采取适当的处理方式
        return render(request, '404.html')
    
    # 获取当前用户的朋友列表
    friends = current_user_profile.friends

    # 返回 friends.html 模板，并传递朋友列表和当前用户名
    return render(request, 'friends.html', {
        'friends': friends,
        'current_user_profile': current_user_profile,
    })