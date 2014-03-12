from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse

from provider.oauth2.models import Client
from braces.views import LoginRequiredMixin

from .forms import AppCreateForm
from .models import Application


class AppCreateView(LoginRequiredMixin, CreateView):
    form_class = AppCreateForm
    template_name = 'applications/application_create.html'

    def get_success_url(self):
        return reverse('admin:dashboard')

    def form_valid(self, form):
        form.instance.creator = self.request.user
        client = Client.objects.create(
            user=form.instance.creator,
            name=form.instance.name,
            client_type=0,
            url=form.instance.download_url,
            redirect_uri=form.instance.redirect_url
        )

        form.instance.client = client
        return super(AppCreateView, self).form_valid(form)


class AppSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'applications/application_settings.html'

    def get_context_data(self, app_id, **kwargs):
        context = super(AppSettingsView, self).get_context_data(**kwargs)

        app = Application.objects.get_single(self.request.user, app_id)
        context['app'] = app

        return context
