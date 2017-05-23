"""Views for social interactions."""

from django.shortcuts import render_to_response, render
from django.template.loader import get_template
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from django.contrib import messages

from braces.views import LoginRequiredMixin
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from allauth.socialaccount.providers import registry

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

from .models import SocialInteraction, SocialInteractionPull
from .base import FREQUENCY, STATUS

import tweepy


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


class SocialInteractionSettings(LoginRequiredMixin, SocialInteractionContext,
            TemplateView):

    """
    Provides the form to update the social interaction settings.
    """
    template_name = 'socialinteractions/socialinteraction_settings.html'

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
        context = super(SocialInteractionSettings, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        print "arredeu", SocialInteractionPull.objects.all()

        context["auth_users"] = auth_users
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
                socialinteraction.socialaccount = SocialAccount.objects.get(
                    pk=data.get('socialaccount'))
                socialinteraction.save()

                messages.success(self.request, 'The social interaction has been updated.')

        return self.render_to_response(context)


class SocialInteractionPost(LoginRequiredMixin, SocialInteractionContext,
                            TemplateView):
    """Provide the form to update the social interaction settings."""

    template_name = 'socialinteractions/socialinteraction_post.html'

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
        context = super(SocialInteractionPost, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        socialinteraction = context.get('socialinteraction')
        sa = socialinteraction.socialaccount
        context['socialaccount'] = sa
        return context


    def post(self, request, project_id, socialinteraction_id):
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
        context = self.get_context_data(project_id, socialinteraction_id)
        socialinteraction = context.get('socialinteraction')

        socialinteraction.text_to_post = data.get('text_post')
        socialinteraction.save()

        return self.render_to_response(context)



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
        print "works works works"
        data = request.POST
        context = self.get_context_data(project_id)

        # socialinteraction = context.get('socialinteraction')

        # socialinteraction.text_to_post = data.get('text_post')
        # socialinteraction.save()


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

            socialinteraction = SocialInteractionPull.objects.create(
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
                mark_safe('The social interaction has been created.<a href="%s"> Add another social interaction.</a>' % add_another_url)
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
            print "socialinteraction_pull", socialinteraction_pull.text_to_pull

        except:
            messages.error(
                self.request, 'The social interactin is not found.'
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

        for i in context:
            print "u" , i
        auth_users = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=['twitter', 'facebook'])

        context["auth_users"] = auth_users
        print "pagasgashas", type(FREQUENCY)
        freq = ['5min', '10min', '20min', '30min','hourly', 'daily','weekly', 'monthly',  'forthnightly']
        status_types = ['active', 'inactive']
        context['status_types'] = status_types
        context["freq"] = freq

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
        context = self.get_context_data(project_id, socialinteractionpull_id)
        si_pull = context['socialinteraction_pull']

        text_pull = data.get("text_pull")
        frequency = data.get('frequency')
        socialaccount_id = data.get('socialaccount')
        socialaccount = SocialAccount.objects.get(id=socialaccount_id)

        status = data.get('status_type')
        print "status", status

        if text_pull != si_pull.text_to_pull:
            si_pull.text_to_pull = text_pull
        if si_pull.frequency != frequency:
            si_pull.frequency = frequency
        if si_pull.socialaccount == socialaccount:
            si_pull.socialaccount = socialaccount
        if si_pull.status != status:
            print "ole ole"
            si_pull.status = status
        si_pull.save()

        print "frequency after", si_pull.frequency

        socialaccount = si_pull.socialaccount
        print "OOOOO", text_pull, frequency, socialaccount

        # socialaccount = SocialAccount.objects.get(id=socialaccount.id)
        # provider = socialaccount.provider
        # app = SocialApp.objects.get(provider=provider)
        # access_token = SocialToken.objects.get(
        #     account__id=socialaccount.id,
        #     account__user=socialaccount.user,
        #     account__provider=app.provider
        # )

        # all_tweets = pull_from_social_media_workshop(
        #     provider,
        #     access_token,
        #     text_pull,
        #     app)
        # from .utils import start2pull

        # start2pull()


        # geometry = all_tweets[0]['geometry']
        # point = 'POINT(' + str(geometry['coordinates'][0]) + ' ' + str(geometry['coordinates'][1]) +')'
        # new_loc = Location.objects.create(
        #     geometry=point,
        #     creator=socialaccount.user
        # )

        # if len(all_tweets) > 1:
        #     try:
        #         print "try"
        #         tweet_cat = Category.objects.get(name='tweetsffff')
        #         print "category", tweet_cat
        #     except:
        #         print "except"
        #         tweet_cat = Category.objects.create(
        #             name='tweeffffffdts',
        #             project=project,
        #             creator=socialaccount.user)
        #     text_field = TextField.objects.create(category=tweet_cat)
        # #text_field = Field.objects.filter(category=tweet_cat)
        # for geo_tweet in all_tweets:
        #     coordinates = geo_tweet['geometry']['coordinates']
        #     point = 'POINT(' + str(coordinates[0]) + ' ' + str(coordinates[1]) +')'
        #     #text_field.value = geo_tweet['text']
        #     #print "text_field", text_field.value
        #     new_loc = Location.objects.create(
        #         geometry=point,
        #         creator=socialaccount.user)
        #     new_observation = Observation.objects.create(
        #         location=new_loc,
        #         project=project,
        #         creator=socialaccount.user,
        #         category=tweet_cat)
        #     properties = {
        #         text_field.key: geo_tweet['text']
        #     }
        #     new_observation.properties = properties
        #     new_observation.save()

        #     # if 'url' in geo_tweet:
        #     #     print "yujuu URL"
        #     #     MediaFile.objects.create(
        #     #         name="tweet",
        #     #         contribution=new_observation.id,
        #     #         creator=socialaccount.user
        #     #     )
        #     # new_comment = Comment.objects.create(
        #     #     text=geo_tweet['text'],
        #     #     commentto=new_observation,
        #     #     creator_id=socialaccount.user.id)
        #     # new_comment.save()
        # context['logs'] = all_tweets
        # print "merda pa tots"
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
            print "hehe"
        except:
            messages.error(
                self.request, 'The social account is not found.'
            )
            return redirect(
                'base.html',
                project_id=project_id,
                socialinteractionpull_id=socialinteractionpull_id
            )

        if socialinteraction_pull:
            if socialinteraction_pull.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social interaction cannot be deleted.'
                )
                return redirect(
                    'admin:socialinteraction_settings',
                    project_id=project_id,
                    socialinteractionpull_id=socialinteractionpull_id
                )
            else:
                socialinteraction_pull.delete()
                messages.success(self.request, 'The social interaction has been'
                    ' deleted.')
                return redirect('admin:socialinteraction_list',
                    project_id=project_id)

        return self.render_to_response(context)




def pull_from_social_media_workshop(provider,access_token,text_to_pull,app):
    """
    Pull data from the timeline when social account has been mentioned and
    with specific text or hastag.

    Parameters
    -----------
    provider =  str
        provider of the social account

    access_token: str - SocialToken Object
        access token for the social account and user
    text_to_pull: str
        text to be searched on the tweets
    app: socialAccount app object

    Returns
    --------
    all_tweets: array
        array of tweet objects

    """

    if provider == 'twitter':
        consumer_key = app.client_id
        consumer_secret = app.secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token_all = access_token
        access_token = access_token_all.token
        access_token_secret = access_token_all.token_secret
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        try:
            # tweets_all = api.home_timeline(count=100)
            tweets_all = api.mentions_timeline(count=100)
            # tweets_all = api.search(q=text_to_pull)
        except:
            print "You are not autheticate"

        all_tweets = []
        for mention in tweets_all:
            new_contribution = {}
            if text_to_pull in mention.text:
                if mention.coordinates:
                    new_contribution = {}
                    new_contribution['text'] = mention.text
                    new_contribution['user'] = mention.user.name
                    new_contribution['created_at'] = mention.created_at
                    new_contribution['geometry'] =  mention.coordinates
                    if 'media' in mention.entities: ## gets when is media attached to it
                        for image in mention.entities['media']:
                            print "yes"
                            new_contribution['url'] = image['url']

                    all_tweets.append(new_contribution)

    return all_tweets

def pull_from_social_media(provider,access_token,text_to_pull,app):
    """This function checks the provider."""

    if provider == 'twitter':
        consumer_key = app.client_id
        consumer_secret = app.secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token_all = access_token
        access_token = access_token_all.token
        access_token_secret = access_token_all.token_secret
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        try:
            # tweets_all = api.mentions_timeline(count=100)
            print "ofoao0", text_to_pull
            # tweets_all = api.search(q="#Brexit", geocode="51.5074 -0.1278 100mi", count=100)
            tweets_all = api.search(q="#Brexit")
        except:
            print "You are not autheticate"

        all_tweets = []
        for mention in tweets_all:
            new_contribution = {}
            print mention.id
            new_contribution['text'] = mention.text
            new_contribution['user'] = mention.user.name
            new_contribution['created_at'] = mention.created_at
            if mention.coordinates: ## checks if there are coorindates
                if text_to_pull in mention.text:
                    #new_contribution['text'] = mention.text
                    geotype = mention.coordinates['type']
                    lon = mention.coordinates['coordinates'][1]
                    lat = mention.coordinates['coordinates'][0]
                    new_contribution['geometry'] = {"lat":lat, "lon":lon}

                    print "\t", lat,lon, geotype
                    if 'media' in mention.entities: ## gets when is media attached to it
                        for image in mention.entities['media']:
                            print "\t","\t","yee", mention.id, image['url']
                            new_contribution['url'] = image['url']
            all_tweets.append(new_contribution)


    # if provider == 'facebook':

    #     try:
    #         graph = facebook.GraphAPI(access_token)
    #     except:
    #         print "You are not autheticate"


    #     objects = graph.get_object("me")
    #     print "I am ", objects
    #     feeds = graph.get_connections("me","feed")
    #     posts = graph.request(objects['id']+'/posts')
    #     feeds = graph.request(objects['id']+'/feed?limit=1000')
    #     print "PPPPPPPP", len(feeds['data'])
    #     print "PPPPPPPP", len(posts['data'])

    #     ##wwww =  graph.request('q=samsung&type=post&center=12.9833,77.5833&distance=1000')
    #     # for w in wwww:
    #     #     print "AHHAHHA", w
    #     for feed in feeds['data']:
    #         print "oo", feed['created_time']
    #         if text_to_pull in feed['message']:
    #             print "Yeeepa", feed['created_time']

    return all_tweets
