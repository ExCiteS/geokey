"""Models for subsets."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

from geokey.contributions.models import Observation, Comment

import tweepy
import facebook

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
    socialaccounts = models.ManyToManyField(
        SocialAccount,
        related_name='socialinteractions',
        through='SocialAccounts'
    )

    text_to_post = models.TextField(blank=True, null=True)

    @classmethod
    def create(cls, name, description, project, socialaccounts, creator):
        """
        Creates a new social interaction and adds the creator and selected
        social accounts asociated to this project

        name : str
            Name of the project
        description : str
            Long-form description of the project
        project : project object
            project object
        socialaccounts : list
            list of social accounts ids associated to this social interaciton
        creator : str
            Indicates if all you users who have access can contribute to the
            project

            Accepted:
            true - all users who have access, including anonymous
            auth - all user who are authenticated
            false - users need to be member of a user group

        Return
        ------
        geokey.socialinteractions.models.SocialInteraction.
        
        """
        if socialaccounts:
            socialinteraction = cls(
                name=name,
                description=description,
                project=project,
                creator=creator,
                text_to_post="New contribution added!!"
            )

            socialinteraction.save()
            for sa in socialaccounts:
                socialinteraction.socialaccounts.add(sa)

            return socialinteraction
        else:
            return

    def update(self, socialinteraction_id, name, description, socialaccounts):
        """
        Updates social interaction

        Parameters
        -----------
        socialinteraction_id : int
            UID of the social interaction
        name :  str
            name of the social interaction
        description: str
            long-form description of the social interaction
        socialaccounts: list
            list of socialaccount ids to be added to the social interaction

        returns
        --------
        geokey.socialinteractions.models.SocialInteraction

        """
        if self:

            self.description = description
            self.name = name
            self.save()
            all_socialccounts = self.socialaccounts.all()
            sa_added = [s for s in socialaccounts]
            sa_exist = [i for i in all_socialccounts]
            to_add = set(sa_added) - set(sa_exist)
            to_remove = set(sa_exist) - set(sa_added)

            for sa_id in to_add:
                self.socialaccounts.add(sa_id)
            for sa_id in to_remove:
                self.socialaccounts.remove(sa_id)
        return self


class SocialAccounts(models.Model):
    """Stores a relation between an interaction and account."""
    socialinteraction = models.ForeignKey(
        'SocialInteraction',
        related_name='socialaccount_of'
    )
    socialaccount = models.ForeignKey(
        SocialAccount,
        related_name='has_socialaccount'
    )

    class Meta:
        auto_created = True
        ordering = ['socialinteraction__name']
        unique_together = ('socialinteraction', 'socialaccount')


@receiver(post_save, sender=Observation)
def post_social_media(sender, instance, created, **kwargs):
    """This function post/tweet to social media when a new Observation
     is added.
    At the same time adds a new comment on the observaction with the link to
    redirect 
     """
    if created:
        project = instance.project
        socialinteractions_all = project.socialinteractions.all()
        url = 'www.acb.com/admin/projects/{project_id}/contributions/{subset_id}/'
        link = url.format(project_id=project.id,subset_id=instance.id)

        for socialinteraction in socialinteractions_all:
            text_to_post = socialinteraction.text_to_post
            replacements = {
                "$project$": project.name,
                "$link$":link
            }

            for key, replacement in replacements.iteritems():
                text_to_post = text_to_post.replace(key, replacement)

            for socialaccount in socialinteraction.socialaccounts.all():

                provider = socialaccount.provider
                app = SocialApp.objects.get(provider=provider)

                access_token = SocialToken.objects.get(
                    account__id = socialaccount.id,
                    account__user=socialaccount.user,
                    account__provider=app.provider
                )
                [tweet_id,screen_name] = check_provider(
                    provider,
                    access_token,
                    text_to_post,
                    app)
                comment_txt = 'https://twitter.com/{user_name}/status/{tweet_id}'.format(
                        user_name=screen_name,
                        tweet_id=tweet_id
                    )
                Comment.objects.create(
                    text=comment_txt,
                    commentto=instance,
                    creator=socialaccount.user
                )

    

def check_provider(provider,access_token,text_to_post,app):
    """This function checks the provider.
    
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