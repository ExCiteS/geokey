from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse

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
        return super(ApplicationCreate, self).form_valid(form)


class ApplicationSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the Application Settings page.
    `/admin/apps/settings`
    """
    template_name = 'applications/application_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, app_id, **kwargs):
        """
        Returns the context data for the page. If the user is not owner of the
        requested application, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_admin` decorator and an error message is
        displayed.
        """
        context = super(ApplicationSettings, self).get_context_data(**kwargs)

        app = Application.objects.as_owner(self.request.user, app_id)
        context['app'] = app

        return context


# ############################################################################
#
# AJAX API views
#
# ############################################################################


class ApplicationUpdate(APIView):
    """
    AJAX API endpoint for updating and deleting applications.
    `/ajax/apps/:app_id`
    """
    @handle_exceptions_for_ajax
    def put(self, request, app_id, format=None):
        """
        Updates an application. If the user is not owner of the
        requested application, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 returned.
        """
        app = Application.objects.as_owner(self.request.user, app_id)

        serializer = AppSerializer(app, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, app_id, format=None):
        """
        Updates an application. If the user is not owner of the
        requested application, `PermissionDenied` is caught and handled in the
        `handle_exceptions_for_ajax` decorator and an error 403 returned.
        """
        app = Application.objects.as_owner(self.request.user, app_id)
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
