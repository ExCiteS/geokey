from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from provider.oauth2.models import Client, AccessToken

from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from .forms import AppCreateForm
from .models import Application
from .serializer import AppSerializer


# ############################################################################
#
# Admin views
#
# ############################################################################


class ApplicationOverview(LoginRequiredMixin, TemplateView):
    """
    Displays an overview of all apps a developer has registered
    `/admin/apps/`
    """
    template_name = 'applications/application_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        context = super(ApplicationOverview, self).get_context_data(**kwargs)
        context['apps'] = Application.objects.get_list(self.request.user)
        return context


class ApplicationCreate(LoginRequiredMixin, CreateView):
    """
    Displays the Create Application page.
    `/admin/apps/register`
    """
    form_class = AppCreateForm
    template_name = 'applications/application_create.html'

    def get_success_url(self):
        """
        Returns the redirect url to be called after successful app registering
        """
        return reverse(
            'admin:app_settings',
            kwargs={'app_id': self.object.id}
        )

    def form_valid(self, form):
        """
        Is called if the form is valid.
        """
        client = Client.objects.create(
            user=self.request.user,
            name=form.instance.name,
            client_type=1,
            url=form.instance.download_url,
            redirect_uri=form.instance.redirect_url
        )
        form.instance.client = client
        form.instance.creator = self.request.user
        messages.success(self.request, "The application has been created.")
        return super(ApplicationCreate, self).form_valid(form)


class ApplicationSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the Application Settings page.
    `/admin/apps/settings`
    """
    template_name = 'applications/application_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, app_id, **kwargs):
        app = Application.objects.as_owner(self.request.user, app_id)
        users = AccessToken.objects.values('user').filter(
            client=app.client).distinct().count()
        return super(ApplicationSettings, self).get_context_data(
            application=app, users=users, **kwargs)

    def post(self, request, app_id):
        context = self.get_context_data(app_id)
        app = context.pop('application')
        data = request.POST

        app.name = data.get('name')
        app.description = data.get('description')
        app.download_url = data.get('download_url')
        app.redirect_url = data.get('redirect_url')
        app.save()

        messages.success(self.request, "The application has been updated.")
        context['application'] = app
        return self.render_to_response(context)


class ApplicationDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, app_id, **kwargs):
        app = Application.objects.as_owner(self.request.user, app_id)
        return super(ApplicationDelete, self).get_context_data(
            application=app, **kwargs)
    
    def get(self, request, app_id):
        context = self.get_context_data(app_id)
        app = context.pop('application', None)

        if app is not None:
            app.delete()

            messages.success(self.request, "The application has been deleted.")
            url = reverse('admin:app_overview')
            return HttpResponseRedirect(url)

        return self.render_to_response(context)        
