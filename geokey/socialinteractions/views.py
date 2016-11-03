"""Views for social interactions."""

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin
from allauth.socialaccount.models import SocialAccount

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

from .models import SocialInteraction


class SocialInteractionList(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Displays the list of social interactions in the project.
    """
    template_name = 'socialinteractions/socialinteraction_list.html'


class SocialInteractionCreate(LoginRequiredMixin, ProjectContext, TemplateView):

    """
    Provides the form to create a new social interaction.
    """
    template_name = 'socialinteractions/socialinteraction_create.html'

    def get_context_data(self, *args, **kwargs):
        
        context = super(SocialInteractionCreate, self).get_context_data( 
            *args,
            **kwargs
        )

        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        context["auth_users"] = auth_users
        return context


    def post(self, request, project_id):
        """
        Creates the social interaction based on the data entered by the user.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to social interaction create if social interaction is 
            created, social interaction list if project is locked or it does 
            not have any categories
        django.http.HttpResponse
            Rendered template, if project does not exist
        """

        data = request.POST
        context = self.get_context_data(project_id)
        project = context.get('project')

        if project:
            cannot_create = 'New social interactions cannot be created.'

            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. %s' % cannot_create
                )
                return redirect(
                    'admin:socialinteraction_create',
                    project_id=project_id
                )

            try:
                socialaccount = SocialAccount.objects.get(
                    pk=data.get('socialaccount'))
            except SocialAccount.DoesNotExist:
                messages.error(
                    self.request,
                    'The social account is not found. %s' % cannot_create
                )
                return redirect(
                    'admin:socialinteraction_create',
                    project_id=project_id
                )

            socialinteraction = SocialInteraction.objects.create(
                name=strip_tags(data.get('name')),
                description=strip_tags(data.get('description')),
                creator=request.user,
                project=project,
                socialaccount=socialaccount,
            )

            add_another_url = reverse(
                'admin:socialinteraction_create',
                kwargs={
                    'project_id': project_id
                }
            )

            messages.success(
                self.request,
                mark_safe('The social interaction has been created.<a href="%s"> Add another social interaction.</a>' % add_another_url)
            )

            return redirect(
                'admin:socialinteraction_settings',
                project_id=project_id,
                socialinteraction_id=socialinteraction.id
            )
        else:
            return self.render_to_response(context)

class SocialInteractionContext(object):

    """
    Provides the context to render templates. The context contains
    a social interaction instance based on project_id and socialinteraction_id.
    """

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, socialinteraction_id, *args, **kwargs):
        """
        Returns the context containing the project and social interaction 
        instances.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database
        socialinteraction_id : int
            Identifies the social interaction in the database

        Returns
        -------
        dict
            Context
        """

        project = Project.objects.as_admin(self.request.user, project_id)

        try:
            socialinteraction = project.socialinteractions.get(
                    pk=socialinteraction_id)

        except:
            messages.error(
                self.request, 'The social interactin is not found.'
                )
            return redirect(
                    'socialinteractions/socialinteraction_settings.html',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id,
                 )

        if socialinteraction:
            return super(SocialInteractionContext, self).get_context_data(
            project=project,
            socialinteraction=socialinteraction,
            )

class SocialInteractionSettings(LoginRequiredMixin, SocialInteractionContext, 
            TemplateView):

    """
    Provides the form to update the social interaction settings.
    """
    template_name = 'socialinteractions/socialinteraction_settings.html'

    def post(self, request, project_id, socialinteraction_id):
        """
        Updates the social interaction based on the data entered by the user.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        socialinteraction_id : int
            Identifies the scoial interaction in the database

        Returns
        -------
        django.http.HttpResponse
            Rendered template when social interactions updated
        django.http.HttpResponse
            Rendered template, if project or social interaction does not exist
        """

        data = request.POST
        try:
            context = self.get_context_data(project_id, socialinteraction_id)
            socialinteraction = context.get('socialinteraction')
        except:
            messages.error(
                self.request, 'The social account is not found.'
                )
            return redirect(
                    'socialinteractions/socialinteraction_settings.html',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )

        if socialinteraction:
            if socialinteraction.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social interaction cannot be deleted.'
                )
                return redirect(
                    'admin:socialinteraction_settings',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )
            else:
                socialinteraction.name = strip_tags(data.get('name'))
                socialinteraction.description = strip_tags(data.get('description'))
                #socialinteraction.socialaccount = socialaccount
                socialinteraction.save()

                messages.success(self.request, 'The social interaction has been updated.')

        return self.render_to_response(context)


class SocialInteractionDelete(LoginRequiredMixin, SocialInteractionContext,
            TemplateView):

    """
    Deletes the social interactions.
    """
    template_name = 'base.html'

    def get(self, request, project_id, socialinteraction_id):
        """
        Deletes the social interaction.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request
        project_id : int
            Identifies the project in the database
        socialinteraction_id : int
            Identifies the social interaction in the database

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to social interaction list if social interaction is 
            deleted, social interaction settings if project is locked, if social
            interaction does not exists redirect to base.html and show error
        django.http.HttpResponse
            Rendered template, if project or social interaction does not exist
        """

        try:
            context = self.get_context_data(project_id, socialinteraction_id)
            socialinteraction = context.get('socialinteraction')

        except:
            messages.error(
                self.request, 'The social account is not found.'
                )
            return redirect(
                    'base.html',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )

        if socialinteraction:
            if socialinteraction.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social interaction cannot be deleted.'
                )
                return redirect(
                    'admin:socialinteraction_settings',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )
            else:
                socialinteraction.delete()                    
                messages.success(self.request, 'The social interaction has been'
                    ' deleted.')
                return redirect('admin:socialinteraction_list', 
                    project_id=project_id)

        return self.render_to_response(context)
