from django.shortcuts import render
from django.http import HttpResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 暫時只返回一個 HttpResponse，不處理登錄邏輯
        return HttpResponse(f"Username: {username}, Password: {password}")
    return render(request, 'login/login.html')
