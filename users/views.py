from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.views import View
from .forms import UserRegisterForm, UserLoginForm
from django.contrib import messages


class Register(View):
    def get(self, request):
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration succeed")
            return redirect('login')
        else:
            messages.error(request, 'Registration failed')
            return render(request, 'users/register.html', {'form': form})


class UserLogin(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'users/login.html', {"form": form})

    def post(self, request):
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main')
        return render(request, 'users/login.html', {"form": form})


