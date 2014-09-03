from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.contrib import messages

from braces.views import LoginRequiredMixin
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from provider.oauth2.models import Client

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
            kwargs={'pk': self.object.id}
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
        return super(ApplicationCreate, self).form_valid(form)


class ApplicationSettings(LoginRequiredMixin, UpdateView):
    """
    Displays the Application Settings page.
    `/admin/apps/settings`
    """
    form_class = AppCreateForm
    model = Application
    fields = ['name', 'description', 'download_url', 'redirect_url']
    template_name = 'applications/application_settings.html'

    def get_success_url(self):
        """
        Returns the redirect url to be called after successful app updating
        """
        return reverse(
            'admin:app_settings',
            kwargs={'pk': self.object.id}
        )

    def form_valid(self, form):
        messages.success(
            self.request, "The application has been updated successfully")
        return super(ApplicationSettings, self).form_valid(form)  

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Returns the context data for the page. If the user is not owner of the
        requested application, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_admin` decorator and an error message is
        displayed.
        """
        return super(ApplicationSettings, self).get_context_data(**kwargs)


class ApplicationDelete(LoginRequiredMixin, TemplateView):
    template_name = 'applications/application_delete.html'

    @handle_exceptions_for_admin
    def get_context_data(self, app_id, **kwargs):
        app = Application.objects.as_owner(self.request.user, app_id)
        app.delete()

        context = super(ApplicationDelete, self).get_context_data(**kwargs)
        context['application'] = app
        return context
