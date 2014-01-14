from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

from opencomap.apps.backend.serializers import SingleSerializer
from opencomap.apps.backend import views as view


def index(request):
    return render(request, 'index.html', RequestContext(request))

def signin(request):
    if request.method == 'GET':
        if request.GET and request.GET['next']: 
            return render(request, 'login.html', RequestContext(request, {'reason': 'required', 'next': request.GET['next']}))
        else:
            return render(request, 'login.html', RequestContext(request))

    elif request.method == 'POST':
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            
            if request.GET and request.GET['next']:
                return redirect(request.GET['next'])
            else:
                return redirect('/admin/dashboard')
        else:
            if request.GET and request.GET['next']:
                return render(request, 'login.html', RequestContext(request, {'reason': 'required', 'next': request.GET['next']}))
            else:
                return render(request, 'login.html', RequestContext(request))

def signout(request):
    logout(request)
    return render(request, 'login.html', RequestContext(request, {'reason': 'logout'}))

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', RequestContext(request))

    elif request.method == 'POST':
        User.objects.create_user(request.POST['email'], request.POST['email'], request.POST['password'], last_name=request.POST['lastname'], first_name=request.POST['firstname']).save()
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('/admin/dashboard')
        
@login_required
def dashboard(request):
    return render(request, 'dashboard.html', RequestContext(request, {"projects": view.projects_list(request.user)}))