from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm
from .models import UserProfile

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # 這裡是重定向到一個新的視圖函數，welcome是該視圖函數的名稱
            return redirect('welcome')
        else:
            # 如果登入失敗，可以重定向回登入頁面或者顯示錯誤信息
            return render(request, 'login/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login/login.html')

# def welcome(request):
#     # 從request中獲取已登入的用戶資訊
#     if request.user.is_authenticated:
#         username = request.user.username
#         return render(request, 'login/welcome.html', {'username': username})
#     else:
#         return redirect('login')

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             new_user = form.save(commit=False)
#             new_user.set_password(form.cleaned_data['password'])
#             new_user.save()
#             # 登录新用户
#             login(request, new_user)
#             return redirect('welcome')  # 重定向到欢迎页面或其他页面
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'login/register.html', {'form': form})

# def welcome(request):
#     if request.user.is_authenticated:
#         user = request.user
#         # 使用 get_or_create 来避免 RelatedObjectDoesNotExist 错误
#         profile, created = UserProfile.objects.get_or_create(user=user)
#         context = {
#             'username': user.username,
#             'profile': profile,
#         }
#         return render(request, 'login/welcome.html', context)
#     else:
#         return redirect('login')

from django.contrib.auth.decorators import login_required

@login_required
def welcome(request):
    # 尝试获取UserProfile，如果不存在，则创建一个空的UserProfile实例
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    context = {
        'username': request.user.username,
        'profile': profile,
    }
    return render(request, 'login/welcome.html', context)



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            # 创建UserProfile实例
            profile = UserProfile.objects.create(user=new_user)
            profile.destination = form.cleaned_data['destination']
            profile.age = form.cleaned_data['age']
            profile.exchange_school = form.cleaned_data['exchange_school']
            profile.date = form.cleaned_data['date']
            profile.gender = form.cleaned_data['gender']
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            # 登录新用户...
            return redirect('welcome')
    else:
        form = UserRegistrationForm()
    return render(request, 'login/register.html', {'form': form})