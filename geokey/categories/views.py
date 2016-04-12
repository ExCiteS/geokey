"""Views for categories."""

from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.views import ProjectContext
from geokey.core.decorators import handle_exceptions_for_ajax

from .base import STATUS
from .models import (
    Category, Field, TextField, NumericField, LookupField, LookupValue,
    MultipleLookupField, MultipleLookupValue
)
from .forms import CategoryCreateForm, FieldCreateForm
from .serializers import (
    CategorySerializer, FieldSerializer, LookupFieldSerializer
)
from geokey.categories.mixins import CategoryMixin, FieldMixin
from geokey.contributions.models import Observation


# #############################################################################
#
# ADMIN VIEWS
#
# #############################################################################

class CategoryList(LoginRequiredMixin, ProjectContext, TemplateView):
    """A list of all categories page."""

    template_name = 'categories/category_list.html'


class CategoryCreate(LoginRequiredMixin, ProjectContext, CreateView):
    """Create category page."""

    template_name = 'categories/category_create.html'
    form_class = CategoryCreateForm

    def get_context_data(self, **kwargs):
        """
        Return the context to render the view.

        Overwrite the method to add the project to the context.

        Returns
        -------
        dict
            Context.
        """
        return super(CategoryCreate, self).get_context_data(
            self.kwargs['project_id'],
            **kwargs
        )

    def form_valid(self, form):
        """
        Create a new category when form is valid.

        Parameters
        ----------
        form : geokey.categories.forms.CategoryCreateForm
            Represents the user input.
        """
        data = form.cleaned_data
        project = Project.objects.as_admin(
            self.request.user,
            self.kwargs['project_id']
        )

        if project:
            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. New categories cannot be created.'
                )
                return redirect(
                    'admin:category_create',
                    project_id=self.kwargs['project_id']
                )
            else:
                category = Category.objects.create(
                    project=project,
                    creator=self.request.user,
                    name=strip_tags(data.get('name')),
                    description=strip_tags(data.get('description')),
                    default_status=data.get('default_status')
                )

                add_another_url = reverse(
                    'admin:category_create',
                    kwargs={'project_id': self.kwargs['project_id']}
                )
                messages.success(
                    self.request,
                    mark_safe('The category has been created. <a href="%s"> '
                              'Add another category.</a>' % add_another_url)
                )
                return redirect(
                    'admin:category_overview',
                    project_id=self.kwargs['project_id'],
                    category_id=category.id
                )

        return self.render_to_response(self.get_context_data(form=form))


class CategoryOverview(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Category overview page."""

    template_name = 'categories/category_overview.html'


class CategorySettings(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Category settings page."""

    template_name = 'categories/category_settings.html'

    def get_context_data(self, project_id, category_id):
        """
        Return the context to render the view.

        Overwrites the method to a number of contributions for the category and
        available status types to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        dict
            Context.
        """
        context = super(CategorySettings, self).get_context_data(
            project_id,
            category_id,
            status_types=STATUS,
        )
        category = context.get('category')

        if category:
            context['num_contributions'] = Observation.objects.filter(
                category=category
            ).count()

        return context

    def post(self, request, project_id, category_id):
        """
        Update category settings.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        django.http.HttpResponse
            Rendered template.
        """
        data = request.POST
        context = self.get_context_data(project_id, category_id)
        category = context.get('category')

        if category:
            category.name = strip_tags(data.get('name'))
            category.description = strip_tags(data.get('description'))
            category.default_status = data.get('default_status')

            if category.fields.exists():
                display_field = category.fields.get(
                    pk=data.get('display_field')
                )

                if category.display_field != display_field:
                    category.display_field = display_field
                    for observation in category.observation_set.all():
                        observation.update_display_field()
                        observation.save()

            category.save()
            messages.success(self.request, 'The category has been updated.')
            context['category'] = category

        return self.render_to_response(context)


class CategoryDisplay(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Category display page."""

    template_name = 'categories/category_display.html'

    def post(self, request, project_id, category_id):
        """
        Update category display.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        django.http.HttpResponse
            Rendered template.
        """
        data = request.POST
        context = self.get_context_data(project_id, category_id)
        category = context.get('category')

        if category:
            symbol = request.FILES.get('symbol')
            category.colour = data.get('colour')

            if symbol is not None:
                category.symbol.delete()
                category.symbol = symbol
            elif data.get('clear-symbol') == 'true':
                category.symbol.delete()
                category.symbol = None

            category.save()
            messages.success(
                self.request,
                'The display settings have been updated'
            )
            context['category'] = category

        return self.render_to_response(context)


class CategoryDelete(LoginRequiredMixin, CategoryMixin, TemplateView):
    """Delete category page."""

    template_name = 'base.html'

    def get(self, request, project_id, category_id):
        """
        Delete the category.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to category list if category is deleted, category
            settings if project is locked.
        django.http.HttpResponse
            Rendered template, if project or category does not exist.
        """
        context = self.get_context_data(project_id, category_id)
        category = context.get('category')

        if category:
            if category.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Category cannot be deleted.'
                )
                return redirect(
                    'admin:category_settings',
                    project_id=project_id,
                    category_id=category_id
                )
            else:
                category.delete()
                messages.success(
                    self.request,
                    'The category has been deleted.'
                )
                return redirect('admin:category_list', project_id=project_id)

        return self.render_to_response(context)


class FieldCreate(LoginRequiredMixin, CategoryMixin, CreateView):
    """Creat field page."""

    template_name = 'categories/field_create.html'
    form_class = FieldCreateForm

    def get_context_data(self, data=None, **kwargs):
        """
        Return the context to render the view.

        Overwrite the method to add available field types the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        dict
            Context.
        """
        context = super(FieldCreate, self).get_context_data(
            self.kwargs['project_id'],
            self.kwargs['category_id'],
            **kwargs
        )
        context['fieldtypes'] = Field.get_field_types()
        return context

    def form_valid(self, form):
        """
        Create a new field when form is valid.

        Parameters
        ----------
        form : geokey.categories.forms.FieldCreateForm
            Represents the user input.
        """
        request = self.request
        data = form.cleaned_data
        category = Category.objects.as_admin(
            self.request.user,
            self.kwargs['project_id'],
            self.kwargs['category_id']
        )

        if category:
            if category.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. New fields cannot be created.'
                )
                return redirect(
                    'admin:category_field_create',
                    project_id=self.kwargs['project_id'],
                    category_id=self.kwargs['category_id']
                )
            else:
                proposed_key = slugify(strip_tags(data.get('name')))
                if len(proposed_key) < 1:
                    proposed_key = 'key'
                suggested_key = proposed_key

                count = 1
                while category.fields.filter(key=suggested_key).exists():
                    suggested_key = '%s-%s' % (proposed_key, count)
                    count = count + 1

                field = Field.create(
                    strip_tags(data.get('name')),
                    suggested_key,
                    strip_tags(data.get('description')),
                    data.get('required'),
                    category,
                    request.POST.get('type')
                )

                if isinstance(field, TextField):
                    field.textarea = request.POST.get('textarea') or False
                    field.maxlength = request.POST.get('maxlength') or None

                elif isinstance(field, NumericField):
                    field.minval = request.POST.get('minval') or None
                    field.maxval = request.POST.get('maxval') or None

                field.save()

                add_another_url = reverse(
                    'admin:category_field_create',
                    kwargs={
                        'project_id': self.kwargs['project_id'],
                        'category_id': self.kwargs['category_id']
                    }
                )
                messages.success(
                    self.request,
                    mark_safe('The field has been created. <a href="%s">Add '
                              'another field.</a>' % add_another_url)
                )
                return redirect(
                    'admin:category_field_settings',
                    project_id=self.kwargs['project_id'],
                    category_id=self.kwargs['category_id'],
                    field_id=field.id
                )

        return self.render_to_response(self.get_context_data(form=form))


class FieldSettings(LoginRequiredMixin, FieldMixin, TemplateView):
    """Field settings page."""

    template_name = 'categories/field_settings.html'

    def get_context_data(self, project_id, category_id, field_id, **kwargs):
        """
        Return the context to render the view.

        Overwrites the method to add available field types to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.
        field_id : int
            Identifies the field in the database.

        Returns
        -------
        dict
            Context
        """
        context = super(FieldSettings, self).get_context_data(
            project_id,
            category_id,
            field_id
        )

        if context.get('field'):
            context['status_types'] = STATUS
            context['is_display_field'] = (
                context['field'] == context['field'].category.display_field)

        return context

    def post(self, request, project_id, category_id, field_id):
        """
        Update field settings.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.
        field_id : int
            Identifies the field in the database.

        Returns
        -------
        django.http.HttpResponse
            Rendered template.
        """
        data = request.POST
        context = self.get_context_data(
            project_id,
            category_id,
            field_id
        )
        field = context.get('field')

        if field:
            field.name = strip_tags(data.get('name'))
            field.description = strip_tags(data.get('description'))
            field.required = data.get('required') or False

            if isinstance(field, TextField):
                field.textarea = data.get('textarea') or False
                field.maxlength = data.get('maxlength') or None
            elif isinstance(field, NumericField):
                field.minval = data.get('minval') or None
                field.maxval = data.get('maxval') or None

            field.save()
            messages.success(self.request, 'The field has been updated.')
            context['field'] = field

        return self.render_to_response(context)


class FieldDelete(LoginRequiredMixin, FieldMixin, TemplateView):
    """Delete field page."""

    template_name = 'base.html'

    def get(self, request, project_id, category_id, field_id):
        """
        Delete the field.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.
        field_id : int
            Identifies the field in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to category overview if field is deleted, field
            settings if project is locked.
        django.http.HttpResponse
            Rendered template, if project, category or field does not exist.
        """
        context = self.get_context_data(project_id, category_id, field_id)
        field = context.get('field')

        if field:
            if field.category.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Field cannot be deleted.'
                )
                return redirect(
                    'admin:category_field_settings',
                    project_id=project_id,
                    category_id=category_id,
                    field_id=field_id
                )
            else:
                field.delete()
                messages.success(self.request, 'The field has been deleted.')
                return redirect(
                    'admin:category_overview',
                    project_id=project_id,
                    category_id=category_id
                )

        return self.render_to_response(context)


# #############################################################################
#
# AJAX API
#
# #############################################################################

class CategoryUpdate(APIView):

    """
    API endpoints for a category in the AJAX API.
    """

    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        """
        Handles the GET request.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        category = Category.objects.as_admin(
            request.user, project_id, category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id):
        """
        Handles the POST request and updates the category.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        category = Category.objects.as_admin(
            request.user, project_id, category_id)

        serializer = CategorySerializer(
            category, data=request.data, partial=True,
            fields=('id', 'name', 'description', 'status'))

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldUpdate(APIView):

    """
    API endpoints for fields.
    """

    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id, field_id,
            format=None):
        """
        Handles the POST request and updates the category

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database
        field_id : int
            Identifies the field in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)

        serializer = FieldSerializer(
            field, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FieldLookups(APIView):

    """
    API endpoint for lookupvalues.
    """

    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id, field_id,
             format=None):
        """
        Handles the POST request and adds a lookupvalue to the field.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database
        field_id : int
            Identifies the field in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)
        name = strip_tags(request.data.get('name'))

        if field.category.project.islocked:
            return Response(
                {'error': 'The project is locked.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(field, LookupField):
            LookupValue.objects.create(name=name, field=field)

            serializer = LookupFieldSerializer(field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif isinstance(field, MultipleLookupField):
            MultipleLookupValue.objects.create(name=name, field=field)

            serializer = LookupFieldSerializer(field)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'This field is not a lookup field.'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldLookupsUpdate(APIView):

    """
    API endpoint for lookupvalues.
    """

    def get_field(self, user, project_id, category_id, field_id):
        field = Field.objects.as_admin(
            user, project_id, category_id, field_id)

        if (isinstance(field, LookupField) or
                isinstance(field, MultipleLookupField)):
            return field
        else:
            return None

    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id, field_id, value_id):
        """
        Handles the POST request and updates the lookupvalue symbol.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database
        field_id : int
            Identifies the field in the database
        value_id : int
            Identifies the lookupvalue in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        field = self.get_field(request.user, project_id, category_id, field_id)

        if field:
            if field.category.project.islocked:
                return Response(
                    {'error': 'The project is locked.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                value = field.lookupvalues.get(pk=value_id)

                name = request.data.get('name')

                if name:
                    value.name = strip_tags(name)

                symbol = request.FILES.get('symbol')

                if symbol:
                    value.symbol.delete()
                    value.symbol = symbol
                elif request.POST.get('clear-symbol') == 'true':
                    value.symbol.delete()
                    value.symbol = None

                value.save()

                return Response({
                    'id': value.id,
                    'name': value.name,
                    'symbol': value.symbol.url if value.symbol else None
                })
        else:
            return Response(
                {'error': 'This field is not a lookup field.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, category_id, field_id, value_id):
        """
        Handles the DELETE request and removes the lookupvalue the category.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request
        project_id : int
            Identifies the project in the database
        category_id : int
            Identifies the category in the database
        field_id : int
            Identifies the field in the database
        value_id : int
            Identifies the lookupvalue in the database

        Return
        ------
        rest_framework.response.Response
            Response to the request
        """

        field = self.get_field(request.user, project_id, category_id, field_id)

        if field:
            if field.category.project.islocked:
                return Response(
                    {'error': 'The project is locked.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                field.lookupvalues.get(pk=value_id).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'This field is not a lookup field.'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldsReorderView(APIView):
    """Ajax API to reorder fields of a category."""

    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id):
        """
        Handle POST request.

        Reorder fields of the category.

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        rest_framework.response.Response
            Response to the request.
        """
        category = Category.objects.as_admin(
            request.user,
            project_id,
            category_id
        )

        try:
            category.reorder_fields(request.data.get('order'))
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Field.DoesNotExist:
            return Response(
                {'error': 'One or more field IDs were not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ############################################################################
#
# PUBLIC API
#
# ############################################################################

class SingleCategory(APIView):
    """Public API for a single category."""

    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        """
        Handle GET request.

        Return the complete category (including all fields).

        Parameters
        ----------
        request : rest_framework.request.Request
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        category_id : int
            Identifies the category in the database.

        Returns
        -------
        rest_framework.response.Response
            Response to the request.
        """
        category = Category.objects.get_single(
            request.user,
            project_id,
            category_id
        )
        serializer = CategorySerializer(category)
        return Response(serializer.data)
