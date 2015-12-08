from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.views import ProjectContext
from geokey.core.decorators import (
    handle_exceptions_for_ajax, handle_exceptions_for_admin
)

from .base import STATUS
from .models import (
    Category, Field, TextField, NumericField, LookupField, LookupValue,
    MultipleLookupField, MultipleLookupValue
)
from .forms import CategoryCreateForm, FieldCreateForm
from .serializers import (
    CategorySerializer, FieldSerializer, LookupFieldSerializer
)
from geokey.contributions.models import Observation


class CategoryContext(object):
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, *args, **kwargs):
        category = Category.objects.as_admin(
            self.request.user, project_id, category_id)

        return super(CategoryContext, self).get_context_data(
            category=category,
            *args,
            **kwargs
        )


class FieldContext(object):
    @handle_exceptions_for_admin
    def get_context_data(self, project_id, category_id, field_id,
                         *args, **kwargs):
        field = Field.objects.as_admin(
            self.request.user, project_id, category_id, field_id)

        return super(FieldContext, self).get_context_data(
            field=field,
            *args,
            **kwargs
        )


# ############################################################################
#
# Administration views
#
# ############################################################################

class CategoryList(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Displays a list of all catgories for a given project.
    """
    template_name = 'categories/category_list.html'


class CategoryOverview(LoginRequiredMixin, CategoryContext, TemplateView):
    """
    Landing page when a user clicks on a category. Displays a lis of fields
    assigned to the category.
    """
    template_name = 'categories/category_overview.html'


class CategoryCreate(LoginRequiredMixin, ProjectContext, CreateView):
    """
    Displays the create Category page and creates the Category
    when POST is requested
    """
    form_class = CategoryCreateForm
    template_name = 'categories/category_create.html'

    def get_context_data(self, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the project.

        Returns
        -------
        dict
            context; {'project': <geokey.projects.models.Project>}
        """
        project_id = self.kwargs['project_id']

        return super(CategoryCreate, self).get_context_data(
            project_id, **kwargs
        )

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the category.

        Parameters
        ----------
        form : geokey.categories.forms.CategoryCreateForm
            Represents the user input
        """
        data = form.cleaned_data

        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        category = Category.objects.create(
            project=project,
            creator=self.request.user,
            name=strip_tags(data.get('name')),
            description=strip_tags(data.get('description')),
            default_status=data.get('default_status')
        )

        messages.success(self.request, "The category has been created.")
        return redirect(
            'admin:category_overview',
            project_id=project.id,
            category_id=category.id
        )


class CategorySettings(LoginRequiredMixin, CategoryContext, TemplateView):
    """
    Displays the category settings page
    """
    template_name = 'categories/category_settings.html'

    def get_context_data(self, project_id, category_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the category.

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Returns
        -------
        dict
            {
                'category': <geokey.categories.models.Category>
                'status_types': List of status types for categoies
                'num_contributions': Number of contributions of that category
            }
        """
        context = super(CategorySettings, self).get_context_data(
            project_id,
            category_id,
            status_types=STATUS,
        )

        if context.get('category'):
            context['num_contributions'] = Observation.objects.filter(
                category=context['category']).count()

        return context

    def post(self, request, project_id, category_id):
        """
        Handles the POST request and updates the category

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)

        if category is not None:
            data = request.POST

            category.name = strip_tags(data.get('name'))
            category.description = strip_tags(data.get('description'))
            category.default_status = data.get('default_status')

            if category.fields.exists():
                display_field = category.fields.get(
                    pk=data.get('display_field')
                )

                if category.display_field != display_field:
                    category.display_field = display_field
                    for obs in category.observation_set.all():
                        obs.update_display_field()
                        obs.save()

            category.save()

            messages.success(self.request, "The category has been updated.")
            context['category'] = category
        return self.render_to_response(context)


class CategoryDisplay(LoginRequiredMixin, CategoryContext, TemplateView):
    """
    Displat the category display settings, i.e. where colour and icon for the
    category can be set.
    """
    template_name = 'categories/category_display.html'

    def post(self, request, project_id, category_id):
        """
        Handles the POST request and updates the category display settings

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)

        if category is not None:
            data = request.POST
            symbol = request.FILES.get('symbol')
            category.colour = data.get('colour')

            if symbol is not None:
                category.symbol = symbol
            elif data.get('clear-symbol') == 'true':
                category.symbol = None

            category.save()

            messages.success(
                self.request, 'The display settings have been updated')
            context['category'] = category

        return self.render_to_response(context)


class CategoryDelete(LoginRequiredMixin, CategoryContext, TemplateView):
    """
    Deletes a category if requesting user is admin of the project
    """
    template_name = 'base.html'

    def get(self, request, project_id, category_id):
        """
        Handles the GET request and deletes the category

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to list of categories overview.

        django.http.HttpResponse
            If user is not admin of the project, the error message is rendered.
        """
        context = self.get_context_data(project_id, category_id)
        category = context.pop('category', None)

        if category is not None:
            category.delete()

            messages.success(self.request, "The category has been deleted.")
            return redirect('admin:category_list', project_id=project_id)

        return self.render_to_response(context)


class FieldCreate(LoginRequiredMixin, CategoryContext, CreateView):
    """
    Displays the create field page
    """
    form_class = FieldCreateForm
    template_name = 'categories/field_create.html'

    def get_context_data(self, data=None, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the category and available field types

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Returns
        -------
        dict
            {
                'category': <geokey.categories.models.Category>
                'fieldtypes': List of str, representing the field types
            }
        """
        project_id = self.kwargs['project_id']
        category_id = self.kwargs['category_id']

        context = super(FieldCreate, self).get_context_data(
            project_id, category_id, **kwargs)

        context['fieldtypes'] = Field.get_field_types()
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the field.

        Parameters
        ----------
        form : geokey.categories.forms.FieldCreateForm
            Represents the user input

        Return
        ------
        Redirects to field setting page of the created field
        """
        project_id = self.kwargs['project_id']
        category_id = self.kwargs['category_id']
        data = form.cleaned_data
        category = Category.objects.as_admin(
            self.request.user, project_id, category_id)

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
            self.request.POST.get('type')
        )

        if isinstance(field, TextField):
            field.textarea = self.request.POST.get('textarea') or False
            field.maxlength = self.request.POST.get('maxlength') or None

        elif isinstance(field, NumericField):
            field.minval = self.request.POST.get('minval') or None
            field.maxval = self.request.POST.get('maxval') or None

        field.save()

        field_create_url = reverse(
            'admin:category_field_create',
            kwargs={
                'project_id': project_id,
                'category_id': category_id
            }
        )

        messages.success(
            self.request,
            mark_safe('The field has been created. <a href="%s">Add another '
                      'field.</a>' % field_create_url)
        )

        return redirect(
            'admin:category_field_settings',
            project_id=category.project.id,
            category_id=category.id,
            field_id=field.id
        )


class FieldSettings(LoginRequiredMixin, FieldContext, TemplateView):
    """
    Displays the field settings page
    """
    template_name = 'categories/field_settings.html'

    def get_context_data(self, project_id, category_id, field_id, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the field and available field types

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database

        Returns
        -------
        dict
            {
                'field': <geokey.categories.models.Field>
                'status_types': List of str, representing the status types
                'is_display_field : Boolean, indicates if field is display
                    field
            }
        """
        context = super(FieldSettings, self).get_context_data(
            project_id, category_id, field_id)

        if context.get('field'):
            context['status_types'] = STATUS
            context['is_display_field'] = (
                context['field'] == context['field'].category.display_field)

        return context

    def post(self, request, project_id, category_id, field_id):
        """
        Handles the POST request and updates the field

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(
            project_id,
            category_id,
            field_id
        )
        field = context.pop('field', None)

        if field is not None:
            data = request.POST

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

            messages.success(self.request, "The field has been updated.")
            context['field'] = field

        return self.render_to_response(context)


class FieldDelete(LoginRequiredMixin, FieldContext, TemplateView):
    template_name = 'base.html'

    def get(self, request, project_id, category_id, field_id):
        """
        Handles the GET request and deletes the field

        Parameter
        ---------
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to list of fields overview.

        django.http.HttpResponse
            If user is not admin of the project, the error message is rendered.
        """
        context = self.get_context_data(project_id, category_id, field_id)
        field = context.pop('field', None)

        if field is not None:
            field.delete()

            messages.success(self.request, "The field has been deleted.")
            return redirect(
                'admin:category_overview',
                project_id=project_id,
                category_id=category_id
            )

        return self.render_to_response(context)


# ############################################################################
#
# AJAX API views
#
# ############################################################################

class CategoryUpdate(APIView):
    """
    API Endpoints for a category in the AJAX API.
    /ajax/projects/:project_id/categories/:category_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        """
        Handles the GET request

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        category = Category.objects.as_admin(
            request.user, project_id, category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id):
        """
        Handles the POST request and updates the category

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
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
    API endpoints for fields
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id
    """
    @handle_exceptions_for_ajax
    def put(self, request, project_id, category_id, field_id,
            format=None):
        """
        Handles the POST request and updates the category

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
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
    API endpoint for lookupvalues
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id/lookupvalues
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id, field_id,
             format=None):
        """
        Handles the POST request and adds a lookupvalue to the field

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        field = Field.objects.as_admin(
            request.user, project_id, category_id, field_id)
        name = strip_tags(request.data.get('name'))

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
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldLookupsUpdate(APIView):
    """
    API endpoint for lookupvalues
    /ajax/projects/:project_id/categories/:category_id/fields/
    :field_id/lookupvalues/:value_id
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
    def patch(self, request, project_id, category_id, field_id, value_id):
        """
        Handles the PATCH request and updates the lookupvalue

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database
        value_id : int
            Identifier of the lookupvalue in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        field = self.get_field(request.user, project_id, category_id, field_id)

        if field:
            val = field.lookupvalues.get(pk=value_id)
            val.name = strip_tags(request.data.get('name'))
            val.save()

            return Response({"id": val.id, "name": val.name})
        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )

    @handle_exceptions_for_ajax
    def delete(self, request, project_id, category_id, field_id, value_id):
        """
        Handles the DELETE request and removes the lookupvalue the category

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database
        field_id : int
            Identifier of the field in the database
        value_id : int
            Identifier of the lookupvalue in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        field = self.get_field(request.user, project_id, category_id, field_id)

        if field:
            field.lookupvalues.get(pk=value_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'This field is not a lookup field'},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldsReorderView(APIView):
    """
    API endpoint to reorder the fields of a category
    /ajax/projects/:project_id/categories/:category_id/fields/re-order/
    """
    @handle_exceptions_for_ajax
    def post(self, request, project_id, category_id):
        """
        Handles the DELETE request and removes the lookupvalue the category

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        category = Category.objects.as_admin(
            request.user, project_id, category_id)
        try:
            category.re_order_fields(request.data.get('order'))

            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Field.DoesNotExist:
            return Response(
                {'error': 'One or more field ids where not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ############################################################################
#
# Public API views
#
# ############################################################################

class SingleCategory(APIView):
    """
    API endpoint for a single category
    /api/projects/:project_id/categories/:category_id
    """
    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        """
        Handles the GET request and returns the complete category including
        all fields

        Parameter
        ---------
        request : rest_framework.request.Request
            Object reprensting the request
        project_id : int
            Identifier of the project in the database
        category_id : int
            Identifier of the category in the database

        Return
        ------
        rest_framework.response.Response
            Reponse to the request
        """
        category = Category.objects.get_single(
            request.user, project_id, category_id)

        serializer = CategorySerializer(category)
        return Response(serializer.data)
