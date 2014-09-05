from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.contrib import messages

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from projects.models import Project
from core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from .base import STATUS
from .models import (
    ObservationType, Field, NumericField, LookupField, LookupValue
)
from .forms import ObservationTypeCreateForm, FieldCreateForm
from .serializer import (
    ObservationTypeSerializer, FieldSerializer,
    NumericFieldSerializer, LookupFieldSerializer
)


# ############################################################################
#
# Administration views
#
# ############################################################################

class CategoryList(LoginRequiredMixin, TemplateView):
    template_name = 'observationtypes/category_list.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user

        context = super(CategoryList, self).get_context_data()
        context['project'] = Project.objects.as_admin(user, project_id)

        return context


class CategoryOverview(LoginRequiredMixin, TemplateView):
    template_name = 'observationtypes/category_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id):
        """
        Creates the request context for rendering the page
        """
        user = self.request.user
        category = ObservationType.objects.as_admin(
            user, project_id, category_id)

        context = super(CategoryOverview, self).get_context_data()
        context['category'] = category

        return context


class ObservationTypeCreate(LoginRequiredMixin, CreateView):
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
            ObservationTypeCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def get_success_url(self):
        """
        Returns the redeirect URL after successful creation of the
        observation type
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:observationtype_settings',
            kwargs={
                'project_id': project_id, 'observationtype_id': self.object.id
            }
        )

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)
        form.instance.project = project
        messages.success(self.request, "The category has been created.")
        return super(ObservationTypeCreate, self).form_valid(form)


class ObservationTypeSettings(LoginRequiredMixin, TemplateView):
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
        observation_type = ObservationType.objects.as_admin(
            user, project_id, observationtype_id)
        return {
            'observationtype': observation_type,
            'admin': observation_type.project.is_admin(user),
            'status_types': STATUS
        }

    def post(self, request, project_id, observationtype_id):
        context = self.get_context_data(project_id, observationtype_id)
        category = context.pop('observationtype')
        data = request.POST
        print data

        category.name = data.get('name')
        category.description = data.get('description')
        category.save()

        messages.success(self.request, "The category has been updated.")
        context['observationtype'] = category
        return self.render_to_response(context)


class CategoryDelete(LoginRequiredMixin, TemplateView):
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, **kwargs):
        user = self.request.user
        category = ObservationType.objects.as_admin(
            user, project_id, category_id)
        return super(CategoryDelete, self).get_context_data(
            category=category, **kwargs)

    def get(self, request, project_id, category_id):
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)

        if category is not None:
            category.delete()

            messages.success(self.request, "The category has been deleted.")
            return redirect('admin:category_list', project_id=project_id)

        return self.render_to_response(context)     
        


class FieldCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create field page
    """
    form_class = FieldCreateForm
    template_name = 'observationtypes/field_create.html'

    @handle_exceptions_for_admin
    def get_context_data(self, form, data=None, key_error=False, **kwargs):
        project_id = self.kwargs['project_id']
        observationtype_id = self.kwargs['observationtype_id']

        context = super(FieldCreate, self).get_context_data(**kwargs)

        context['category'] = ObservationType.objects.as_admin(
            self.request.user, project_id, observationtype_id
        )
        context['fieldtypes'] = Field.get_field_types()
        context['key_error'] = key_error
        if key_error:
            context['data'] = data
        return context

    def form_valid(self, form):
        project_id = self.kwargs['project_id']
        observationtype_id = self.kwargs['observationtype_id']
        data = form.cleaned_data
        observation_type = ObservationType.objects.as_admin(
            self.request.user, project_id, observationtype_id)

        try:
            field = Field.create(
                data.get('name'),
                data.get('key'),
                data.get('description'),
                data.get('required'),
                observation_type,
                self.request.POST.get('type')
            )
            messages.success(self.request, "The field has been created.")
            return redirect(
                'admin:observationtype_field_settings',
                project_id=observation_type.project.id,
                observationtype_id=observation_type.id,
                field_id=field.id
            )
        except IntegrityError:
            data = form.cleaned_data
            data['type'] = self.request.POST.get('type')
            return self.render_to_response(self.get_context_data(form, data=data, key_error=True))


class FieldSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the field detail page
    """
    template_name = 'observationtypes/field_view.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, observationtype_id, field_id,
                         **kwargs):
        user = self.request.user
        field = Field.objects.get_single(
            user, project_id, observationtype_id, field_id)
        context = super(FieldSettings, self).get_context_data(**kwargs)
        context['field'] = field
        context['status_types'] = STATUS

        return context


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class ObservationTypeUpdate(APIView):
    """
    API Endpoints for a observationtype in the AJAX API.
    /ajax/projects/:project_id/observationtypes/:observationtype_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, observationtype_id, format=None):
        observation_type = ObservationType.objects.as_admin(
            request.user, project_id, observationtype_id)

        serializer = ObservationTypeSerializer(observation_type)
        return Response(serializer.data)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, observationtype_id, format=None):
        """
        Updates an observationtype
        """

        observation_type = ObservationType.objects.as_admin(
            request.user, project_id, observationtype_id)

        serializer = ObservationTypeSerializer(
            observation_type, data=request.DATA, partial=True,
            fields=('id', 'name', 'description', 'status'))

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldUpdate(APIView):
    """
    API endpoints for fields
    /ajax/projects/:project_id/observationtypes/:observationtype_id/fields/
    :field_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, observationtype_id, field_id,
            format=None):
        """
        Updates a field
        """
        field = Field.objects.as_admin(
            request.user, project_id, observationtype_id, field_id)

        if isinstance(field, NumericField):
            serializer = NumericFieldSerializer(
                field, data=request.DATA, partial=True
            )
        else:
            serializer = FieldSerializer(
                field, data=request.DATA, partial=True
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldLookups(APIView):
    """
    API endpoint for lookupvalues
    /ajax/projects/:project_id/observationtypes/:observationtype_id/fields/
    :field_id/lookupvalues
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, observationtype_id, field_id,
             format=None):
        """
        Adds a lookup value to the lookup field
        """
        field = Field.objects.as_admin(
            request.user, project_id, observationtype_id, field_id)

        if isinstance(field, LookupField):
            LookupValue.objects.create(
                name=request.DATA.get('name'), field=field)

            serializer = LookupFieldSerializer(field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldLookupsUpdate(APIView):
    """
    API endpoint for lookupvalues
    /ajax/projects/:project_id/observationtypes/:observationtype_id/fields/
    :field_id/lookupvalues/:value_id
    """
    @handle_exceptions_for_ajax
    def delete(self, request, project_id, observationtype_id, field_id,
               value_id, format=None):
        """
        Removes a LookupValue
        """
        field = Field.objects.as_admin(
            request.user, project_id, observationtype_id, field_id)

        if isinstance(field, LookupField):
            field.lookupvalues.get(pk=value_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


# ############################################################################
#
# Public API views
#
# ############################################################################

class SingleObservationType(APIView):
    """
    API endpoint for a single observationtype
    /api/projects/:project_id/observationtypes/:observationtype_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, observationtype_id, format=None):
        """
        Returns the observationtype and all fields
        """
        observationtype = ObservationType.objects.get_single(
            request.user, project_id, observationtype_id)

        serializer = ObservationTypeSerializer(observationtype)
        return Response(serializer.data)
