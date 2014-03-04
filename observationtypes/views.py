from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from projects.models import Project
from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from .base import STATUS, FIELD_TYPES
from .models import ObservationType, Field
from .forms import ObservationTypeCreateForm, FieldCreateForm
from .serializer import ObservationTypeUpdateSerializer


class ObservationTypeAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create ObservationType page and creates the ObservationType
    when POST is requested
    """
    form_class = ObservationTypeCreateForm
    template_name = 'observationtypes/observationtype_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        """
        Creates the request context for rendering the page
        """
        project_id = self.kwargs['project_id']

        context = super(
            ObservationTypeAdminCreateView, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, pk=project_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        project_id = self.kwargs['project_id']

        data = form.cleaned_data
        project = Project.objects.as_admin(self.request.user, pk=project_id)

        observation_type = ObservationType.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            project=project
        )
        return redirect(
            'admin:observationtype_detail',
            project_id=project.id,
            observationtype_id=observation_type.id
        )


class ObservationTypeAdminDetailView(LoginRequiredMixin, TemplateView):
    """
    Displays the observation type detail page
    """
    template_name = 'observationtypes/observationtype_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, observationtype_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        observation_type = ObservationType.objects.get_single(
            user, project_id, observationtype_id)
        return {
            'observationtype': observation_type,
            'admin': observation_type.project.is_admin(user),
            'status_types': STATUS
        }


class ObservationTypeApiDetail(APIView):
    """
    API Endpoints for a observationtype in the AJAX API.
    /ajax/projects/:project_id/observationtypes/:observationtype_id
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, observationtype_id, format=None):
        """
        Updates an observationtype
        """

        observation_type = ObservationType.objects.as_admin(
            request.user, project_id, observationtype_id)
        serializer = ObservationTypeUpdateSerializer(
            observation_type, data=request.DATA)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldAdminCreateView(LoginRequiredMixin, CreateView):
    """
    Displays the create field page
    """
    form_class = FieldCreateForm
    template_name = 'observationtypes/field_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, **kwargs):
        project_id = self.kwargs['project_id']
        observationtype_id = self.kwargs['observationtype_id']

        context = super(FieldAdminCreateView, self).get_context_data(**kwargs)

        context['observationtype'] = ObservationType.objects.as_admin(
            self.request.user, project_id, observationtype_id
        )
        context['fieldtypes'] = FIELD_TYPES
        return context

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        observationtype_id = self.kwargs['observationtype_id']
        data = form.cleaned_data
        observation_type = ObservationType.objects.as_admin(
            self.request.user, project_id, observationtype_id)

        field = Field.create(
            data.get('name'),
            data.get('key'),
            data.get('description'),
            data.get('required'),
            observation_type,
            self.request.POST.get('type')
        )
        return redirect(
            'admin:observationtype_detail',
            project_id=observation_type.project.id,
            observationtype_id=observation_type.id
        )
