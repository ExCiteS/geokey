"""Views for social interactions."""

from django.views.generic import TemplateView
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
from geokey.contributions.models import (
    Observation,
    Comment,
    Location,
    MediaFile
)

from simple_history.models import HistoricalRecords

from geokey.categories.models import Category

from .models import SocialInteraction
import tweepy
import facebook

from osgeo import ogr


class SocialInteractionList(LoginRequiredMixin, ProjectContext, TemplateView):
    """Display the list of social interactions in the project."""

    template_name = 'socialinteractions/socialinteraction_list.html'

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
        context = super(SocialInteractionList, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )

        if len(socialaccounts) == 0:
            context['socialaccounts_auth'] = ['']
        else:
            context['socialaccounts_auth'] = socialaccounts

        return context


class SocialInteractionCreate(LoginRequiredMixin, ProjectContext,
                              TemplateView):
    """Provide the form to create a new social interaction."""

    template_name = 'socialinteractions/socialinteraction_create.html'

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
        context = super(SocialInteractionCreate, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )

        context['socialaccounts'] = socialaccounts

        return context

    def post(self, request, project_id):
        """
        Create the social interaction based on the data entered by the user.

        Parameters
        ----------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to social interaction settings page if social interaction
            is created, social interaction create page if project is locked or
            social account is not found.
        django.http.HttpResponse
            Rendered template, if project does not exist.
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
            else:
                socialaccount_list = data.getlist('socialaccounts', [])
                socialaccounts = SocialAccount.objects.filter(
                    pk__in=socialaccount_list
                )
                try:
                    socialinteraction = SocialInteraction.create(
                        strip_tags(data.get('name')),
                        strip_tags(data.get('description')),
                        project,
                        socialaccounts,
                        request.user
                    )
                    add_another_url = reverse(
                        'admin:socialinteraction_create',
                        kwargs={
                            'project_id': project_id
                        }
                    )
                    messages.success(
                        self.request,
                        mark_safe('The social interaction has been created. '
                                  '<a href="%s"> Add another social '
                                  'interaction.</a>' % add_another_url)
                    )

                    return redirect(
                        'admin:socialinteraction_settings',
                        project_id=project_id,
                        socialinteraction_id=socialinteraction.id
                    )
                except:
                    messages.error(
                        self.request,
                        'The social account is not found. %s' % cannot_create
                    )
                    return redirect(
                        'admin:socialinteraction_create',
                        project_id=project_id
                    )

        else:
            return self.render_to_response(context)


class SocialInteractionContext(object):
    """Provide the context to render templates."""

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, socialinteraction_id,
                         *args, **kwargs):
        """
        Return the context to render the view.

        Add social interaction to the context.

        Parameters
        ----------
        project_id : int
            Identifies the project in the database.
        socialinteraction_id : int
            Identifies the social interaction in the database.

        Returns
        -------
        dict
            Context.
        """
        project = Project.objects.as_admin(self.request.user, project_id)

        try:
            socialinteraction = project.socialinteractions.get(
                pk=socialinteraction_id)
            return super(SocialInteractionContext, self).get_context_data(
                project=project,
                socialinteraction=socialinteraction,
            )
        except:
            return {
                'error': 'Not found.',
                'error_description': 'The social interaction is not found.'
            }


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
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )
        socialinteraction = context.get('socialinteraction')
        context['socialaccounts'] = socialaccounts
        is_twitter = False
        for sa in socialinteraction.socialaccounts.all():
            if sa.provider == "twitter":
                is_twitter = True
        context['is_twitter']= is_twitter

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


class SocialInteractionSettings(LoginRequiredMixin, SocialInteractionContext,
                                TemplateView):
    """Provide the form to update the social interaction settings."""

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
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )

        if len(socialaccounts) == 0:
            context['socialaccounts_auth'] = ['']
        else:
            context['socialaccounts_auth'] = socialaccounts

        return context

    def post(self, request, project_id, socialinteraction_id):
        """
        Update the social interaction based on the data entered by the user.

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
        if socialinteraction:
            socialaccount_ids = data.getlist('socialaccounts', [])

            socialaccounts = SocialAccount.objects.filter(
                                                pk__in=socialaccount_ids)
            try:
                context['socialinteraction'] = socialinteraction.update(
                    socialinteraction_id,
                    strip_tags(data.get('name')),
                    strip_tags(data.get('description')),
                    socialaccounts
                )
            except:
                pass

        messages.success(
                    self.request,
                    'The social interaction has been updated.'
                )
        return self.render_to_response(context)


class SocialInteractionDelete(LoginRequiredMixin, SocialInteractionContext,
                              TemplateView):
    """Delete the social interaction."""

    template_name = 'base.html'

    def get(self, request, project_id, socialinteraction_id):
        """
        Delete the social interaction.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        socialinteraction_id : int
            Identifies the social interaction in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to social interactions list if social interaction is
            deleted, social interaction settings if project is locked.
        django.http.HttpResponse
            Rendered template, if project or social interaction does not exist.
        """
        context = self.get_context_data(project_id, socialinteraction_id)
        socialinteraction = context.get('socialinteraction')

        if socialinteraction:
            if socialinteraction.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Social interaction cannot be '
                    'deleted.'
                )
                return redirect(
                    'admin:socialinteraction_settings',
                    project_id=project_id,
                    socialinteraction_id=socialinteraction_id
                )
            socialinteraction.delete()

            messages.success(
                self.request,
                'The social interaction has been deleted.'
            )
            return redirect(
                'admin:socialinteraction_list',
                project_id=project_id
            )
        return self.render_to_response(context)


class SocialInteractionPull(LoginRequiredMixin, ProjectContext,
                                TemplateView):
    """Provide the form to pull the data from social media."""

    template_name = 'socialinteractions/socialinteraction_pull.html'

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
        context = super(SocialInteractionPull, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )

        if len(socialaccounts) == 0:
            context['socialaccounts_auth'] = ['']
        else:
            context['socialaccounts_auth'] = socialaccounts

        context['socialaccounts'] = socialaccounts

        return context

    def post(self, request, project_id):
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
        text_pull = data.get("text_pull")
        socialaccount_id= data.get('socialaccount_id')
        socialaccount = SocialAccount.objects.get(id=socialaccount_id)
        provider = socialaccount.provider
        app = SocialApp.objects.get(provider=provider)
        access_token = SocialToken.objects.get(
                account__id = socialaccount.id,
                account__user=socialaccount.user,
                account__provider=app.provider
            )
        
        
        all_tweets = pull_from_social_media(provider,access_token,text_pull,app)
        
        context = self.get_context_data(project_id)                

        context['all_tweets'] = all_tweets

        return self.render_to_response(context)



class SocialInteractionPullWorkshop(LoginRequiredMixin, ProjectContext,
                                TemplateView):
    """Provide the form to update the social interaction settings."""

    template_name = 'socialinteractions/socialinteraction_pullWorkshop.html'

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
        context = super(SocialInteractionPullWorkshop, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )
        socialaccounts = SocialAccount.objects.filter(
            user=self.request.user,
            provider__in=[id for id, name in registry.as_choices()
                          if id in ['twitter', 'facebook']]
        )

        if len(socialaccounts) == 0:
            context['socialaccounts_auth'] = ['']
        else:
            context['socialaccounts_auth'] = socialaccounts

        context['socialaccounts'] = socialaccounts

        return context

    def post(self, request, project_id):
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
        context = self.get_context_data(project_id)
        project = context['project']
        text_pull = data.get("text_pull")
        category_id = data.get('category')
        socialaccount_id= data.get('socialaccount_id')
        socialaccount = SocialAccount.objects.get(id=socialaccount_id)
        provider = socialaccount.provider
        app = SocialApp.objects.get(provider=provider)
        access_token = SocialToken.objects.get(
                account__id = socialaccount.id,
                account__user=socialaccount.user,
                account__provider=app.provider
            )       
        
        all_tweets = pull_from_social_media_workshop(provider,access_token,text_pull,app)
        geometry = all_tweets[0]['geometry']
        point  = 'POINT(' + str(geometry['coordinates'][0]) + ' ' + str(geometry['coordinates'][1]) +')' 
        new_loc = Location.objects.create(
            geometry=point,
            creator=socialaccount.user
        )


        for geo_tweet in all_tweets:
            coordinates = geo_tweet['geometry']['coordinates']
            point  = 'POINT(' + str(coordinates[0]) + ' ' + str(coordinates[1]) +')' 
            new_loc = Location.objects.create(
                geometry=point,
                creator=socialaccount.user
            )
            new_observation =  Observation.objects.create(
                location=new_loc,
                project=project,
                creator=socialaccount.user,
                category=Category.objects.get(id=category_id)
            )
            new_observation.save()
            # if 'url' in geo_tweet:
            #     print "yujuu URL"
            #     MediaFile.objects.create(
            #         name="tweet",
            #         contribution=new_observation.id,
            #         creator=socialaccount.user
            #     )



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
            tweets_all = api.mentions_timeline(count=100)
            #tweets_all = api.search(q=text_to_pull)
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
            tweets_all = api.search(q=text_to_pull)
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