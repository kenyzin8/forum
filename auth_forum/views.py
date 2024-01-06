from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib import messages

from .forms import *

def logout_page(request):
    django_logout(request)
    return redirect('forum')

def login_page(request):

    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                django_login(request, user)
                return redirect('forum-page')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            print(form.errors)

    return render(request, 'login.html', {'form': form})