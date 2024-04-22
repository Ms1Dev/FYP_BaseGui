from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm



@login_required(login_url="user-login")
def Index(request):
    return render(request, 'index.html')


def Login(request):
    form = LoginForm()

    context={ 'form': form }

    if request.method == 'POST':
        form = LoginForm(request.POST)
        context["form"] = form

        _username = request.POST.get('username', False)
        _password = request.POST.get('password', False)
        
        user = authenticate(request, username=_username, password=_password)

        if user is not None:
            login(request, user)
            return redirect('index')
        
    return render(request, 'login.html', context)


def Logout(request):
    logout(request)
    return redirect('user-login')