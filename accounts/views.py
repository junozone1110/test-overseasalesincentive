from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def login_view(request):
    """ログイン画面"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'ログインしました。')
            return redirect('dashboard')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """ログアウト"""
    logout(request)
    messages.info(request, 'ログアウトしました。')
    return redirect('login')


@login_required
def profile_view(request):
    """プロフィール画面"""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

