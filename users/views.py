from django.db.models import Q
from django import forms
from django.views.generic import TemplateView, CreateView
from django.contrib import auth
from django.shortcuts import redirect
from django.contrib.auth.models import User

from braces.views import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response

from projects.models import Project
from projects.base import STATUS

from .serializers import UserSerializer


class Index(TemplateView):
    """
    Displays the splash page. Redirects to dashboard if a user is looged in.
    """
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return self.render_to_response(self.get_context_data)
        else:
            return redirect('admin:dashboard')


class Login(TemplateView):
    """
    Displays the login page and handles login requests.
    """
    template_name = 'login.html'

    def get(self, request):
        """
        Displays the page and an optional message if the user has been
        redirected here from anonther page.
        """
        if request.GET and request.GET.get('next'):
            context = self.get_context_data(
                login_required=True,
                next=request.GET.get('next')
            )
        else:
            context = self.get_context_data
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and redirects to next page if available.
        """
        user = auth.authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            auth.login(request, user)
            if request.GET and request.GET.get('next'):
                return redirect(request.GET.get('next'))
            else:
                return redirect('admin:dashboard')
        else:
            context = self.get_context_data(login_failed=True)
            return self.render_to_response(context)


class Logout(TemplateView):
    """
    Displays the logout page
    """
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        """
        Logs the user out
        """
        auth.logout(request)
        return super(Logout, self).get(request, *args, **kwargs)

    def get_context_data(self):
        """
        Return the context data to display the 'Succesfully logged out message'
        """
        return {'logged_out': True}


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', )


class Signup(CreateView):
    """
    Displays the sign-up page
    """
    template_name = 'signup.html'
    form_class = UserRegistrationForm

    def form_valid(self, form):
        """
        Registers the user if the form is valid and no other has been
        regstered woth the username.
        """
        data = form.cleaned_data
        User.objects.create_user(
            data.get('username'),
            data.get('email'),
            data.get('password'),
            last_name=data.get('last_name'),
            first_name=data.get('first_name'),
        ).save()

        user = auth.authenticate(
            username=data.get('username'),
            password=data.get('password')
        )

        auth.login(self.request, user)
        return redirect('admin:dashboard')

    def form_invalid(self, form):
        """
        The form is invalid or another user has already been registerd woth
        that username. Displays the error message.
        """
        context = self.get_context_data(form=form, user_exists=True)
        return self.render_to_response(context)


class Dashboard(LoginRequiredMixin, TemplateView):
    """
    Displays the dashboard.
    """
    template_name = 'dashboard.html'

    def get_context_data(self):
        return {
            'projects': Project.objects.all(self.request.user),
            'status_types': STATUS
        }


class QueryUsers(APIView):
    def get(self, request, format=None):
        q = request.GET.get('query').lower()
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(last_name__icontains=q) |
            Q(first_name__icontains=q))[:10]

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
