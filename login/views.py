from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Iot
from django.contrib import messages
from .forms import UserRegisterForm


def login(request):


    return render(request, 'login/login.html')

def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account Successfully Created')
            return redirect('Login')
    else:
        form = UserRegisterForm()
    return render(request, 'login/register.html',{'form' : form })


def forgot_pass(request):

    return render(request, 'login/forgotpass.html')
