"""
Stole most of the code from from
https://github.com/ianalexander/django-oauth2-tastypie/blob/master/src/authentication.py
"""

import logging

from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from provider.oauth2.models import AccessToken


def verify_access_token(key):
    # Check if key is in AccessToken key
    try:
        token = AccessToken.objects.get(token=key)

        # Check if token has expired
        if token.expires < timezone.now():
            raise OAuthError('AccessToken has expired.')
    except AccessToken.DoesNotExist:
        raise OAuthError("AccessToken not found at all.")

    logging.info('Valid access')
    return token


def is_authenticated(request):
    """
    Verify 2-legged oauth request. Parameters accepted as
    values in "Authorization" header, or as a GET request
    or in a POST body.
    """
    logging.info("OAuth20Authentication")

    try:
        key = request.GET.get('oauth_consumer_key')
        if not key:
            key = request.POST.get('oauth_consumer_key')
        if not key:
            auth_header_value = request.META.get('Authorization')
            if auth_header_value:
                key = auth_header_value.split(' ')[1]
        if not key:
            logging.error('OAuth20Authentication. No consumer_key found.')
            return None
        """
        If verify_access_token() does not pass, it will raise an error
        """
        token = verify_access_token(key)

        # If OAuth authentication is successful, set the request user to
        # the token user for authorization
        request.user = token.user

        # If OAuth authentication is successful, set oauth_consumer_key on
        # request in case we need it later
        request.META['oauth_consumer_key'] = key
        return True
    except KeyError:
        logging.exception("Error in OAuth20Authentication.")
        request.user = AnonymousUser()
        return False
    except Exception:
        logging.exception("Error in OAuth20Authentication.")
        return False
    return True


def oauthenticate(func):
    def wrapped(*args, **kwargs):
        request = args[0]
        if is_authenticated(request):
            return func(*args, **kwargs)

    return wrapped
