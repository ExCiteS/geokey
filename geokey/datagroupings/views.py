import json

from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import strip_tags

from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_admin

from geokey.projects.models import Project
from geokey.categories.models import Category

from .base import STATUS
from .forms import GroupingCreateForm
from .models import Grouping, Rule


# ############################################################################
#
# Administration views
#
# ############################################################################

class GroupingList(LoginRequiredMixin, TemplateView):
    template_name = 'datagroupings/grouping_list.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the project to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database

        Returns
        -------
        dict
            context
        """
        user = self.request.user

        context = super(GroupingList, self).get_context_data()
        context['project'] = Project.objects.as_admin(user, project_id)

        return context


class GroupingCreate(LoginRequiredMixin, CreateView):
    """
    Displays the create view page
    """
    form_class = GroupingCreateForm
    template_name = 'datagroupings/grouping_create.html'

    def get_success_url(self):
        """
        Returns the URL that is called after successfully creating the
        grouping.

        Returns
        -------
        str
            URL that is called
        """
        project_id = self.kwargs['project_id']
        return reverse(
            'admin:grouping_overview',
            kwargs={'project_id': project_id, 'grouping_id': self.object.id}
        )

    @handle_exceptions_for_admin
    def get_context_data(self, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the project to the context.

        Returns
        -------
        dict
            context
        """
        project_id = self.kwargs['project_id']

        context = super(
            GroupingCreate, self).get_context_data(**kwargs)

        context['project'] = Project.objects.as_admin(
            self.request.user, project_id
        )
        return context

    def form_valid(self, form):
        """
        Is called when the POSTed data is valid and creates the observation
        type.

        Parameters
        ----------
        form : geokey.grouings.forms.GroupingCreateForm
            Represents the user input
        """
        project_id = self.kwargs['project_id']
        project = Project.objects.as_admin(self.request.user, project_id)

        form.instance.project = project
        form.instance.creator = self.request.user
        messages.success(self.request, "The data grouping has been created.")
        return super(GroupingCreate, self).form_valid(form)


class GroupingOverview(LoginRequiredMixin, TemplateView):
    """
    Provides an overview of all rules assigned to the grouping.
    """
    template_name = 'datagroupings/grouping_overview.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the grouping to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        dict
            context
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingOverview, self).get_context_data(
            grouping=grouping
        )


class GroupingSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the page to change the settings of the data grouping
    """
    template_name = 'datagroupings/grouping_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the grouping and available status types to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        dict
            context
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return {'grouping': grouping, 'status_types': STATUS}

    def post(self, request, project_id, grouping_id):
        """
        Updates the settings of the data grouping

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, grouping_id)
        grouping = context.pop('grouping', None)

        if grouping is not None:
            data = request.POST

            grouping.name = strip_tags(data.get('name'))
            grouping.description = strip_tags(data.get('description'))
            grouping.save()

            messages.success(self.request, "The data grouping has been updated.")
            context['grouping'] = grouping

        return self.render_to_response(context)


class GroupingPermissions(LoginRequiredMixin, TemplateView):
    """
    Displays the page to change the permissions for the data grouping.
    Permissions are change via Ajax
    """
    template_name = 'datagroupings/grouping_permissions.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the grouping to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        dict
            context
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingPermissions, self).get_context_data(
            grouping=grouping
        )


class GroupingDelete(LoginRequiredMixin, TemplateView):
    """
    Deletes a data grouping
    """
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id):
        """
        Returns the context to render the view. Overwrites the method to add
        the grouping to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        dict
            context
        """
        user = self.request.user
        grouping = Grouping.objects.as_admin(user, project_id, grouping_id)
        return super(GroupingDelete, self).get_context_data(grouping=grouping)

    def get(self, request, project_id, grouping_id):
        """
        Deletes a data grouping

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to list of data groupings overview.

        django.http.HttpResponse
            If user is not administrator of the project, the error message is
            rendered.
        """
        context = self.get_context_data(project_id, grouping_id)
        grouping = context.pop('grouping', None)

        if grouping is not None:
            grouping.delete()
            messages.success(
                self.request,
                'The data grouping has been deleted'
            )

            return redirect('admin:grouping_list', project_id=project_id)

        return self.render_to_response(context)


class RuleCreate(LoginRequiredMixin, CreateView):
    """
    Displays the rule create page
    """
    template_name = 'datagroupings/rule_create.html'
    model = Rule

    @handle_exceptions_for_admin
    def get_context_data(self, *args, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the grouping to the context.

        Returns
        -------
        dict
            context
        """
        self.object = None

        project_id = self.kwargs['project_id']
        grouping_id = self.kwargs['grouping_id']

        context = super(
            RuleCreate, self).get_context_data(*args, **kwargs)

        context['grouping'] = Grouping.objects.as_admin(
            self.request.user, project_id, grouping_id
        )
        return context

    def post(self, request, project_id, grouping_id):
        """
        Creates a new Rule with the POSTed data.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to the rule settings.

        django.http.HttpResponse
            If user is administrator of the project, the error message is
            rendered.
        """
        context = self.get_context_data()
        grouping = context.pop('grouping', None)

        if grouping is not None:
            category = Category.objects.as_admin(
                self.request.user, project_id, request.POST.get('category'))

            rules = None
            min_date = None
            max_date = None

            rules = request.POST.get('rules', None)
            if rules is not None:
                rules = json.loads(rules)
                min_date = rules.pop('min_date')
                max_date = rules.pop('max_date')

            Rule.objects.create(
                grouping=grouping,
                category=category,
                min_date=min_date,
                max_date=max_date,
                constraints=rules
            )
            messages.success(self.request, 'The filter has been created.')
            return redirect('admin:grouping_overview',
                            project_id=project_id, grouping_id=grouping_id)

        return self.render_to_response(context)


class RuleSettings(LoginRequiredMixin, TemplateView):
    """
    Displays the rule settings page
    """
    template_name = 'datagroupings/rule_settings.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id, rule_id, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the rule to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database
        rule_id : int
            identifies the rule in the database

        Returns
        -------
        dict
            context
        """
        context = super(RuleSettings, self).get_context_data(**kwargs)

        view = Grouping.objects.as_admin(
            self.request.user,
            project_id,
            grouping_id
        )

        context['rule'] = view.rules.get(pk=rule_id)
        return context

    @handle_exceptions_for_admin
    def post(self, request, project_id, grouping_id, rule_id):
        """
        Updates the rule.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database
        rule_id : int
            identifies the rule in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template
        """
        context = self.get_context_data(project_id, grouping_id, rule_id)

        rule = context.pop('rule', None)

        if rule is not None:
            rules = request.POST.get('rules', None)
            if rules is not None:
                rules = json.loads(rules)
                rule.min_date = rules.pop('min_date')
                rule.max_date = rules.pop('max_date')
                rule.constraints = rules

            rule.save()
            messages.success(self.request, 'The filter has been updated.')
            return redirect('admin:grouping_overview',
                            project_id=project_id, grouping_id=grouping_id)

        return self.render_to_response(context)


class RuleDelete(LoginRequiredMixin, TemplateView):
    """
    Deletes the rule
    """
    template_name = 'base.html'

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, grouping_id, rule_id, **kwargs):
        """
        Returns the context to render the view. Overwrites the method to add
        the rule to the context.

        Parameter
        ---------
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database
        rule_id : int
            identifies the rule in the database

        Returns
        -------
        dict
            context
        """
        grouping = Grouping.objects.as_admin(
            self.request.user, project_id, grouping_id)
        context = super(RuleDelete, self).get_context_data(**kwargs)

        context['rule'] = grouping.rules.get(pk=rule_id)
        return context

    def get(self, request, project_id, grouping_id, rule_id):
        """
        Deletes the rule

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            identifies the project in the database
        grouping_id : int
            identifies the data grouping in the database
        rule_id : int
            identifies the rule in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            redirecting to list of rules overview.

        django.http.HttpResponse
            If user is administrator of the project, the error message is
            rendered.
        """
        context = self.get_context_data(project_id, grouping_id, rule_id)
        rule = context.pop('rule', None)

        if rule is not None:
            rule.delete()

            messages.success(self.request, 'The filter has been deleted')
            return redirect(
                'admin:grouping_overview',
                project_id=project_id, grouping_id=grouping_id
            )

        return self.render_to_response(context)
