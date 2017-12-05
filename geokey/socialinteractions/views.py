"""Views for social interactions."""

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

from .models import SocialInteractionPost, SocialInteractionPull
from .base import STATUS, FREQUENCY


class SocialInteractionList(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Displays the list of social interactions in the project.
    """
    template_name = 'socialinteractions/socialinteraction_list.html'


class SocialInteractionPostCreate(LoginRequiredMixin, ProjectContext, TemplateView):
    """
    Provides the form to create a new social interaction.
    """
    template_name = 'socialinteractions/socialinteraction_post_create.html'

    def get_context_data(self, *args, **kwargs):

        context = super(SocialInteractionPostCreate, self).get_context_data(
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
                    'admin:socialinteraction_post_create',
                    project_id=project_id
                )

            try:
                socialaccount = SocialAccount.objects.get(
                    pk=data.get('socialaccount'))
                text_to_post = data.get('text_post')
                link = data.get('text_link')
            except SocialAccount.DoesNotExist:
                messages.error(
                    self.request,
                    'The social account is not found. %s' % cannot_create
                )
                return redirect(
                    'admin:socialinteraction_post_create',
                    project_id=project_id
                )

            socialinteraction = SocialInteractionPost.objects.create(
                creator=request.user,
                project=project,
                socialaccount=socialaccount,
                text_to_post=text_to_post,
                link=link,
            )

            add_another_url = reverse(
                'admin:socialinteraction_post_create',
                kwargs={
                    'project_id': project_id
                }
            )

            messages.success(
                self.request,
                mark_safe(
                    'The social interaction has been created.<a href="%s"> Add another social interaction.</a>' % add_another_url)
            )
            return redirect(
                'admin:socialinteraction_list',
                project_id=project_id,
            )

        else:
            return self.render_to_response(context)


class SocialInteractionPostContext(object):
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
            socialinteraction = project.socialinteractions_post.get(
                id=socialinteraction_id)

        except:
            messages.error(
                self.request, 'The social interaction was not found.'
            )
            return redirect(
                'socialinteractions/socialinteraction_post_settings.html',
                project_id=project_id,
                socialinteraction_id=socialinteraction_id,
            )

        try:
            socialaccount = SocialAccount.objects.get(id=socialinteraction.socialaccount_id)
        except:
            messages.error(
                self.request, 'The social account was not found'
            )
            return redirect(
                'socialinteractions/socialinteraction_post_settings.html',
                project_id=project_id,
                socialinteraction_id=socialinteraction_id,
            )

        if socialinteraction and socialaccount:
            return super(SocialInteractionPostContext, self).get_context_data(
                project=project,
                socialinteraction=socialinteraction,
                socialaccount=socialaccount,
            )


class SocialInteractionPostDelete(LoginRequiredMixin, SocialInteractionPostContext,
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
                    'admin:socialinteraction_post_settings',
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


class SocialInteractionPostSettings(LoginRequiredMixin, SocialInteractionPostContext,
                                    TemplateView):
    """
    Provides the form to update the social interaction settings.
    """
    template_name = 'socialinteractions/socialinteraction_post_settings.html'

    def get_context_data(self, project_id, *args, **kwargs):
        """
        Return the context to render the view.

        Add Twitter and Facebook social accounts of a user to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        dict
            Context.
        """
        context = super(SocialInteractionPostSettings, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        context["auth_users"] = auth_users
        context['status_types'] = {value: key for key, value in STATUS}.keys()

        return context

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
                'socialinteractions/socialinteraction_post_settings.html',
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
                    'admin:socialinteraction_post_settings',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )
            else:

                socialinteraction.text_to_post = data.get('text_post')
                socialinteraction.link = data.get('text_link')
                socialinteraction.socialaccount = SocialAccount.objects.get(
                    id=data.get('socialaccount'))
                socialinteraction.status = data.get('status_type')
                socialinteraction.save()

                messages.success(self.request, 'The social interaction has been updated.')

        return self.render_to_response(context)


# class SocialInteractionPost(LoginRequiredMixin, SocialInteractionPostContext,
#                             TemplateView):
#     """Provide the form to update the social interaction settings."""
#
#     template_name = 'socialinteractions/socialinteraction_post.html'
#
#     def get_context_data(self, project_id, *args, **kwargs):
#         """
#         Return the context to render the view.
#
#         Add Twitter and Facebook social accounts of a user to the context.
#
#         Parameters
#         ----------
#         project_id : int
#             Identifies the project in the database.
#
#         Returns
#         -------
#         dict
#             Context.
#         """
#
#         return super(SocialInteractionPost, self).get_context_data(
#             project_id,
#             *args,
#             **kwargs
#         )
#
#     def post(self, request, project_id, socialinteraction_id):
#         """
#         Creates social post base on the data entered by the user.
#
#         Parameters
#         ---------
#         request : django.http.HttpRequest
#             Object representing the request.
#         project_id : intyes
#             Identifies the project in the database.
#         socialinteraction_id : int
#             Identifies the social interaction in the database.
#
#         Returns
#         -------
#         django.http.HttpResponse
#             Rendered template when social interactions updated.
#         django.http.HttpResponse
#             Rendered template, if project or social interaction does not exist.
#         """
#         data = request.POST
#         context = self.get_context_data(project_id, socialinteraction_id)
#         socialinteraction = context.get('socialinteraction')
#         socialinteraction.text_to_post = data.get('text_post')
#         socialinteraction.link = data.get('text_link')
#         socialinteraction.save()
#
#         return self.render_to_response(context)


class SocialInteractionPullCreate(LoginRequiredMixin, ProjectContext,
                                  TemplateView):
    """Provide the form to update the social interaction settings."""

    template_name = 'socialinteractions/socialinteraction_pull_create.html'

    def get_context_data(self, *args, **kwargs):

        context = super(SocialInteractionPullCreate, self).get_context_data(
            *args,
            **kwargs
        )

        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        context["auth_users"] = auth_users
        context["frequencies"] = [x for x, _ in FREQUENCY]
        return context

    def post(self, request, project_id):
        """
        Creates social post base on the data entered by the user.

        Parameters
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : intyes
            Identifies the project in the database.
        socialinteraction_id : int
            Identifies the social interaction in the database.

        Returns
        -------
        django.http.HttpResponse
            Rendered template when social interactions updated.
        django.http.HttpResponse
            Rendered template, if project or social interaction does not exist.
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
                    'admin:socialinteraction_post_create',
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
                    'admin:socialinteraction_post_create',
                    project_id=project_id
                )

            SocialInteractionPull.objects.create(
                text_to_pull=strip_tags(data.get('text_pull')),
                creator=request.user,
                project=project,
                socialaccount=socialaccount,
                frequency=strip_tags(data.get('frequency')),
            )

            add_another_url = reverse(
                'admin:socialinteraction_pull_create',
                kwargs={
                    'project_id': project_id
                }
            )

            messages.success(
                self.request,
                mark_safe(
                    'The social interaction has been created.<a href="%s"> Add pull from social media task.</a>' % add_another_url)
            )

            return redirect(
                'admin:socialinteraction_list',
                project_id=project_id,
            )
        else:
            return self.render_to_response(context)


class SocialInteractionPullContext(object):
    """
    Provides the context to render templates. The context contains
    a social interaction instance based on project_id and socialinteraction_id.
    """

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, socialinteractionpull_id, *args, **kwargs):
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
            socialinteraction_pull = project.socialinteractions_pull.get(
                pk=socialinteractionpull_id)

        except:
            messages.error(
                self.request, 'The social interaction pull is not found.'
            )
            return redirect(
                'socialinteractions/socialinteraction_list.html',
                project_id=project_id
            )

        if socialinteraction_pull:
            return super(SocialInteractionPullContext, self).get_context_data(
                project=project,
                socialinteraction_pull=socialinteraction_pull,
            )


class SocialInteractionPullSettings(LoginRequiredMixin, SocialInteractionPullContext,
                                    TemplateView):
    """Provide the form to update the social interaction settings."""

    template_name = 'socialinteractions/socialinteraction_pull.html'

    def get_context_data(self, project_id, *args, **kwargs):

        context = super(SocialInteractionPullSettings, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        context["auth_users"] = auth_users
        context['status_types'] = {value: key for key, value in STATUS}.keys()
        context["freq"] = [x for x, _ in FREQUENCY]

        return context

    def post(self, request, project_id, socialinteractionpull_id):
        """
        Get the data from the specified social media

        Parameters
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : intyes
            Identifies the project in the database.

        Returns
        -------
        django.http.HttpResponse
            Rendered template when social interactions updated.
        django.http.HttpResponse
            Rendered template, if project or social interaction does not exist.
        """
        data = request.POST
        try:
            context = self.get_context_data(
                project_id,
                socialinteractionpull_id
            )
            si_pull = context['socialinteraction_pull']
        except:
            messages.error(
                self.request, 'The social account is not found.'
            )
            return redirect(
                'socialinteractions/socialinteraction_pull.html',
                project_id=project_id,
                socialinteractionpull_id=socialinteractionpull_id
            )
        if si_pull:
            if si_pull.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social interaction cannot be edited.'
                )
                return redirect(
                    'admin:socialinteraction_pull',
                    project_id=project_id,
                    socialinteractionpull_id=socialinteractionpull_id
                )
            else:
                text_pull = data.get("text_pull")
                frequency = data.get('frequency')
                socialaccount_id = data.get('socialaccount')
                socialaccount = SocialAccount.objects.get(id=socialaccount_id)

                status = data.get('status_type')

                if text_pull != si_pull.text_to_pull:
                    si_pull.text_to_pull = text_pull
                if si_pull.frequency != frequency:
                    si_pull.frequency = frequency
                if si_pull.socialaccount != socialaccount:
                    si_pull.socialaccount = socialaccount
                if si_pull.status != status:
                    si_pull.status = status
                si_pull.save()

                messages.success(self.request, 'The social interaction has been updated.')

        return self.render_to_response(context)


class SocialInteractionPullDelete(LoginRequiredMixin, SocialInteractionPullContext,
                                  TemplateView):
    """
    Deletes the social interactions.
    """
    template_name = 'base.html'

    def get(self, request, project_id, socialinteractionpull_id):
        try:
            context = self.get_context_data(project_id, socialinteractionpull_id)
            socialinteraction_pull = context.get('socialinteraction_pull')
        except:
            messages.error(
                self.request, 'The social account is not found.'
            )
            return redirect(
                'base.html',
                project_id=project_id,
                socialinteractionpull_id=socialinteraction_pull.id
            )

        if socialinteraction_pull:
            if socialinteraction_pull.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social pull cannot be deleted.'
                )
                return redirect(
                    'admin:socialinteraction_pull_settings',
                    project_id=project_id,
                    socialinteractionpull_id=socialinteraction_pull.id
                )
            else:
                socialinteraction_pull.delete()
                messages.success(self.request, 'The social interaction has been'
                                               ' deleted.')
                return redirect('admin:socialinteraction_list',
                                project_id=project_id)

        return self.render_to_response(context)
