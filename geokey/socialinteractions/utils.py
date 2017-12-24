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
from geokey.categories.models import Category, TextField, NumericField, Field
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

        last_checked = si_pull.checked_at if si_pull.checked_at is not None else si_pull.created_at
        check_required = check_dates(last_checked, si_pull.frequency)

        if check_required:
            geo_tweets = pull_from_social_media(
                provider,
                access_token,
                si_pull.text_to_pull,
                si_pull.since_id,
                app)

            si_pull.checked_at = timezone.now()

            if len(geo_tweets) != 0:
                si_pull.since_id = max([x['id'] for x in geo_tweets])
                try:
                    project = si_pull.project
                except:
                    next

                tweet_category, text_field, tweet_id_field = get_category_and_field(
                    project,
                    socialaccount)
                for geo_tweet in geo_tweets:
                    if not Observation.objects.filter(project=project, status='active', properties__contains=geo_tweet['id']):
                        create_new_observation(
                            si_pull,
                            geo_tweet,
                            tweet_category,
                            text_field,
                            tweet_id_field
                        )
            si_pull.save()


def create_new_observation(si_pull, geo_tweet, tweet_category, text_field, tweet_id_field):
    """Create new observation based on the tweet.

    Parameters
    -----------
    si_pull: SocialInteractionPull

    geo_tweet: array of tweets

    tweet_category: Category Object

    text_field: TextField Object
    
    tweet_id_field: TweetID Object
    """
    point = geo_tweet['geometry']
    properties = {
        text_field.key: geo_tweet['text'],
        tweet_id_field.key: geo_tweet['id']
    }

    location = Location(
        geometry=point,
        creator=si_pull.socialaccount.user)

    Observation.create(
        properties=properties,
        location=location,
        project=si_pull.project,
        creator=si_pull.socialaccount.user,
        category=tweet_category,
        status='active')

    si_pull.updated_at = timezone.now()
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
        tweet_category = Category.objects.get(
            name="Tweets",
            project=project)

    except:
        tweet_category = Category.objects.create(
            name="Tweets",
            project=project,
            creator=socialaccount.user)

    if TextField.objects.filter(category=tweet_category, key='tweet'):

        text_field = TextField.objects.get(
            category=tweet_category,
            key='tweet')
    else:
        text_field = TextField.objects.create(
            name='Tweet',
            category=tweet_category,
            key="tweet")

    if NumericField.objects.filter(category=tweet_category, key='tweet-id'):

        tweet_id_field = NumericField.objects.get(
            category=tweet_category,
            key='tweet-id')
    else:
        tweet_id_field = NumericField.objects.create(
            name='Tweet-ID',
            category=tweet_category,
            key='tweet-id'
        )
        field = Field.objects.get(pk=tweet_id_field.field_ptr_id)
        field.order = 1
        field.save()
    tweet_category.display_field = text_field
    tweet_category.save()

    return tweet_category, text_field, tweet_id_field


def pull_from_social_media(provider, access_token, text_to_pull, tweet_id, app):
    """Pull data from the timeline with specific text.

    Parameters
    -----------
    provider =  str
        provider of the social account

    access_token: str - SocialToken Object
        access token for the social account and user
    text_to_pull: str
        text to be searched on the tweets
    tweet_id: int
        searches all tweets with id more recent than tweet_id
    app: socialAccount app object
    Returns
    --------
    geo_tweets: array
        array of geo-referenced tweet objects
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
                tweets_all = api.home_timeline(count=100, since_id=tweet_id, tweet_mode='extended')
            except Exception:
                return "Impossible to get data from the timeline"
        except:
            return "You are not authenticated"

        geo_tweets = []
        for tweet in tweets_all:
            if text_to_pull.lower() in tweet.full_text.lower():
                if tweet.coordinates or tweet.place:
                    new_contribution = {}
                    new_contribution['id'] = tweet.id
                    new_contribution['text'] = tweet.full_text
                    new_contribution['user'] = tweet.user.name
                    new_contribution['created_at'] = tweet.created_at
                    new_contribution['geometry'] = process_location(tweet)
                    geo_tweets.append(new_contribution)
        geo_tweets.reverse()
    return geo_tweets


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
