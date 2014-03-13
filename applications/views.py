from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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

class AppCreateView(LoginRequiredMixin, CreateView):
    form_class = AppCreateForm
    template_name = 'applications/application_create.html'

    def get_success_url(self):
        return reverse(
            'admin:app_settings',
            kwargs={'app_id': self.object.id}
        )

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super(AppCreateView, self).form_valid(form)


class AppSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'applications/application_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, app_id, **kwargs):
        context = super(AppSettingsView, self).get_context_data(**kwargs)

        app = Application.objects.as_owner(self.request.user, app_id)
        context['app'] = app

        return context


# ############################################################################
#
# AJAX API views
#
# ############################################################################


class AppUpdateView(APIView):
    @handle_exceptions_for_ajax
    def put(self, request, app_id, format=None):
        app = Application.objects.as_owner(self.request.user, app_id)

        serializer = AppSerializer(app, data=request.DATA, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions_for_ajax
    def delete(self, request, app_id, format=None):
        app = Application.objects.as_owner(self.request.user, app_id)
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
