"""testing utils."""

# import os
# import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'local_settings.settings'


from allauth.socialaccount.models import SocialToken, SocialApp
from geokey.socialinteractions.models import SocialInteractionPull



import tweepy

# sys.path.append('/vagrant/geokey')
# # sys.path.append('/path/to/project') # these lines only needed if not on path
# os.environ['DJANGO_SETTINGS_MODULE'] = 'local_settings.settings'






def start2pull():

    print "# # # # # #   STARTING THE PULL # # # # # # ", os.getcwd()


    si_pull_all = SocialInteractionPull.objects.all()
    print "si_pull_all", si_pull_all
    for si_pull in si_pull_all:
        if si_pull.status == 'active':
            print "si_pull_id:", si_pull.id, 'text to pull:', si_pull.text_to_pull
            # socialaccount = SocialAccount.objects.get(id=socialaccount.id)
            socialaccount = si_pull.socialaccount
            provider = socialaccount.provider
            app = SocialApp.objects.get(provider=provider)
            access_token = SocialToken.objects.get(
                account__id=socialaccount.id,
                account__user=socialaccount.user,
                account__provider=app.provider
            )

            all_tweets = pull_from_social_media_workshop(
                provider,
                access_token,
                si_pull.text_to_pull,
                app)
            for t in all_tweets:
                print "\t Tweet:", t


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


start2pull()
