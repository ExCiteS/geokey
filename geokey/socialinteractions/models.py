"""Models for subsets."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

import tweepy
import facebook

from geokey.subsets.models import Subset
from geokey.contributions.models import Observation, Comment
from .base import STATUS, FREQUENCY


class SocialInteraction(models.Model):
    """Stores a single social interaction."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(
        'projects.Project',
        related_name='socialinteractions'
    )
    socialaccount = models.ForeignKey(
        SocialAccount,
        related_name='socialinteractions'
    )
    text_to_post = models.TextField(blank=True, null=True)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )


class SocialInteractionPull(models.Model):
    """Stores pull social interaction."""
    project = models.ForeignKey(
        'projects.Project',
        related_name='socialinteractions_pull'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    socialaccount = models.ForeignKey(
        SocialAccount,
        related_name='socialinteractions_pull'
    )
    text_to_pull = models.TextField(blank=True, null=True)
    frequency = models.CharField(
        choices=FREQUENCY,
        default=FREQUENCY.daily,
        max_length=20
    )
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    since_id = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(null=True, auto_now_add=False)


@receiver(post_save, sender=Observation)
def post_social_media(sender, instance, created, **kwargs):
    """Post/tweet to social media when a new Observation is added.

    At the same time adds a new comment on the observaction with the link to
    redirect

    In order to avoid problems when pulling data from social media, only will
    post to social media when a new contribution is added to any category
    different than 'Tweets'
    """
    if created:
        project = instance.project
        socialinteractions_all = project.socialinteractions.all()
        url = 'localados/{project_id}/contributions/{subset_id}/'
        link = url.format(project_id=project.id, subset_id=instance.id)
        # if instance.category.name != 'Tweets':
        for socialinteraction in socialinteractions_all:
            text_to_post = socialinteraction.text_to_post
            replacements = {
                "$project$": project.name,
                "$link$": link
            }

            for key, replacement in replacements.iteritems():
                text_to_post = text_to_post.replace(key, replacement)
            # for socialaccount in socialinteraction.socialaccount:
            socialaccount = socialinteraction.socialaccount
            provider = socialaccount.provider
            app = SocialApp.objects.get(provider=provider)

            access_token = SocialToken.objects.get(
                account__id=socialaccount.id,
                account__user=socialaccount.user,
                account__provider=app.provider
            )
            tweet_id, screen_name = check_provider(
                provider,
                access_token,
                text_to_post,
                app)

            # comment_txt = 'https://twitter.com/{user_name}/status/{tweet_id}'.format(
            #     user_name=screen_name,
            #     tweet_id=tweet_id
            # )
            # Comment.objects.create(
            #     text=comment_txt,
            #     commentto=instance,
            #     creator=socialaccount.user
            # )


def check_provider(provider, access_token, text_to_post, app):
    """Check the provider and authenticate.

    Parameters:
    ------------
    provider :  str
        provider of the social account
    access_token: str - SocialToken Object
        access token for the social account and user
    text_to_post: str
        text which will be posted to social media
    app: socialAccount app object

    returns
    --------
    tweet_id : str
        tweet identifier
    screen_aname: str
        screen name user by twitter user

    """
    if provider == 'facebook':
        graph = facebook.GraphAPI(access_token)
        graph.put_wall_post(message=text_to_post)
    if provider == 'twitter':
        consumer_key = app.client_id
        consumer_secret = app.secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token_all = access_token
        access_token = access_token_all.token
        access_token_secret = access_token_all.token_secret
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        tweet_back = api.update_status(text_to_post)

    return tweet_back.id, tweet_back.author.screen_name
