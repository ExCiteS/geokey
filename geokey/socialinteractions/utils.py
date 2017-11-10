"""utils."""
import os

from django.conf import settings
from django.apps import apps

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings.settings")
django.setup()

import tweepy
import facebook

from allauth.socialaccount.models import SocialToken, SocialApp
from geokey.socialinteractions.models import SocialInteractionPull
from geokey.categories.models import Category, TextField, Field
from geokey.contributions.models import Observation, Location

from datetime import timedelta
from geokey.socialinteractions.base import freq_dic

from django.utils import timezone


def check_dates(updated_at, frequency):
    """Check if data the SI Pull needs to be updated."""

    update = updated_at + timedelta(hours=1)

    now = timezone.now() + timedelta(hours=1)

    diff = (((now - update).total_seconds()) / 3600)

    if diff > freq_dic[frequency]:
        return True
    else:
        return False


def start2pull():
    """Start pulling data from Twitter."""
    print 'start2pull executed intresting'
    si_pull_all = SocialInteractionPull.objects.filter(status='active')
    for si_pull in si_pull_all:
        socialaccount = si_pull.socialaccount
        provider = socialaccount.provider
        app = SocialApp.objects.get(provider=provider)
        access_token = SocialToken.objects.get(
            account__id=socialaccount.id,
            account__user=socialaccount.user,
            account__provider=app.provider
        )

        time_to_check = si_pull.updated_at
        if time_to_check == None:
            time_to_check = si_pull.created_at

        times = check_dates(time_to_check, si_pull.frequency)

        if times == True:
            all_tweets = pull_from_social_media(
                provider,
                access_token,
                si_pull.text_to_pull,
                app)

            try:
                project = si_pull.project
            except:
                next

            tweet_cat, text_field = get_category_and_field(
                project,
                socialaccount)
            for geo_tweet in all_tweets:
                if si_pull.since_id == None:
                    create_new_observation(
                        si_pull,
                        geo_tweet,
                        tweet_cat,
                        text_field)

                    since_at = geo_tweet['id']
                    if int(geo_tweet['id']) > int(since_at):
                        since_at = geo_tweet['id']

                    si_pull.updated_at = timezone.now()
                    si_pull.since_id = since_at
                    si_pull.save()

                else:
                    if int(geo_tweet['id']) > int(si_pull.since_id):
                        create_new_observation(
                            si_pull,
                            geo_tweet,
                            tweet_cat,
                            text_field)

                        since_at = geo_tweet['id']
                        if int(geo_tweet['id']) > int(since_at):
                            since_at = geo_tweet['id']

                        si_pull.updated_at = timezone.now()
                        si_pull.since_id = since_at
                        si_pull.save()


def create_new_observation(si_pull, geo_tweet, tweet_cat, text_field):
    """Create new observation based on the tweet.

    Parameters
    -----------
    si_pull: SocialInteractionPull

    geo_tweet: array of tweets

    tweet_cat: Category Object

    text_field: TextField Object
    """
    point = geo_tweet['geometry']

    new_loc = Location.objects.create(
        geometry=point,
        creator=si_pull.socialaccount.user)
    new_observation = Observation.objects.create(
        location=new_loc,
        project=si_pull.project,
        creator=si_pull.socialaccount.user,
        category=tweet_cat)
    properties = {
        text_field.key: geo_tweet['text']}
    new_observation.properties = properties
    new_observation.save()

    si_pull.updated_at = timezone.now()
    si_pull.since_id = geo_tweet['id']
    si_pull.save()


def get_category_and_field(project, socialaccount):
    """Check if Tweet category exists and text field exists.

    Parameters
    ------------
    project: Project Object

    socialaccount: socialaccount object

    Returns
    --------
    tweet_cat: Category object

    text_field: FieldText object

    """
    try:
        tweet_cat = Category.objects.get(
            name="Tweets",
            project=project)

    except:
        tweet_cat = Category.objects.create(
            name="Tweets",
            project=project,
            creator=socialaccount.user)

    if TextField.objects.filter(category=tweet_cat, name='tweet'):

        text_field = TextField.objects.get(
            category=tweet_cat,
            name='tweet')
    else:
        text_field = TextField.objects.create(
            name='tweet',
            category=tweet_cat)

    return tweet_cat, text_field


def pull_from_social_media(provider, access_token, text_to_pull, app):
    """Pull data from the timeline with specific text.

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
        try:
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
            except Exception:
                return "Implossible to get data from the timeline"
        except:
            return "You are not authenticated"

        all_tweets = []
        for mention in tweets_all:
            new_contribution = {}
            if text_to_pull.lower() in mention.text.lower():
                if mention.coordinates or mention.place:
                    new_contribution = {}
                    new_contribution['id'] = mention.id
                    new_contribution['text'] = mention.text
                    new_contribution['user'] = mention.user.name
                    new_contribution['created_at'] = mention.created_at
                    new_contribution['geometry'] = process_location(mention)

                    if 'media' in mention.entities:  ## gets when is media attached to it
                        for image in mention.entities['media']:
                            new_contribution['url'] = image['url']

                    all_tweets.append(new_contribution)

    return all_tweets


def process_location(tweet):
    """Retrieve coordinates or place coordinates from tweet and converts them into WKT Point or Polygon.

    Parameters
    -----------
    tweet =  JSON
        tweet object returned by API

    Returns
    --------
    wkt_coordinates: str
        coordinates in WKT format
    """
    wkt_coordinates = ""
    if tweet.coordinates:
        coordinates = tweet.coordinates
        wkt_coordinates = 'POINT(' + str(coordinates['coordinates'][0]) + ' ' + str(coordinates['coordinates'][1]) + ')'
    elif tweet.place:
        coordinates = tweet.place.bounding_box.coordinates

        is_point = all(c == coordinates[0] for c in coordinates)
        if is_point:
            wkt_coordinates = 'POINT(' + str(coordinates[0][0][0]) + ' ' + str(coordinates[0][0][1]) + ')'
        else:
            wkt_coordinates = 'POLYGON(' + \
                              str(coordinates[0][0][0]) + ' ' + str(coordinates[0][0][1]) + + ', ' + \
                              str(coordinates[0][1][0]) + ' ' + str(coordinates[0][1][1]) + + ', ' + \
                              str(coordinates[0][2][0]) + ' ' + str(coordinates[0][2][1]) + + ', ' + \
                              str(coordinates[0][3][0]) + ' ' + str(coordinates[0][3][1]) + + ', ' + ')'

    return wkt_coordinates
