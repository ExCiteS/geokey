"""Utils for contributions

This code is base on upload_video sample provided by google here:
 https://github.com/youtube/api-samples/blob/master/python/upload_video.py.
"""


import os

from apiclient.discovery import build
from oauth2client import _helpers
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from apiclient.errors import HttpError
from oauth2client.client import OAuth2WebServerFlow

from argparse import Namespace

import httplib2
import httplib

from django.conf import settings


YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error, IOError, httplib.NotConnected,
    httplib.IncompleteRead, httplib.ImproperConnectionState,
    httplib.CannotSendRequest, httplib.CannotSendHeader,
    httplib.ResponseNotReady, httplib.BadStatusLine
)


@_helpers.positional(2)
def my_flow_from_clientsecrets(client_info, scope, redirect_uri=None,
    message=None, cache=None, login_hint=None, device_uri=None, pkce=None,
    code_verifier=None):
    """Create a Flow from a clientsecrets file.

    Will create the right kind of Flow based on the contents of the
    clientsecrets file or will raise InvalidClientSecretsError for unknown
    types of Flows.

    Args:
        filename: string, File name of client secrets.
        scope: string or iterable of strings, scope(s) to request.
        redirect_uri: string, Either the string 'urn:ietf:wg:oauth:2.0:oob' for
                      a non-web-based application, or a URI that handles the
                      callback from the authorization server.
        message: string, A friendly string to display to the user if the
                 clientsecrets file is missing or invalid. If message is
                 provided then sys.exit will be called in the case of an error.
                 If message in not provided then
                 clientsecrets.InvalidClientSecretsError will be raised.
        cache: An optional cache service client that implements get() and set()
               methods. See clientsecrets.loadfile() for details.
        login_hint: string, Either an email address or domain. Passing this
                    hint will either pre-fill the email box on the sign-in form
                    or select the proper multi-login session, thereby
                    simplifying the login flow.
        device_uri: string, URI for device authorization endpoint. For
                    convenience defaults to Google's endpoints but any
                    OAuth 2.0 provider can be used.

    Returns:
        A Flow object.

    Raises:
        UnknownClientSecretsFlowError: if the file describes an unknown kind of
                                       Flow.
        clientsecrets.InvalidClientSecretsError: if the clientsecrets file is
                                                 invalid.
    """
    try:
        constructor_kwargs = {
            'redirect_uri': redirect_uri,
            'auth_uri': client_info['auth_uri'],
            'token_uri': client_info['token_uri'],
            'login_hint': login_hint,
        }
        revoke_uri = client_info.get('revoke_uri')
        optional = ('revoke_uri', 'device_uri', 'pkce', 'code_verifier')
        for param in optional:
            if locals()[param] is not None:
                constructor_kwargs[param] = locals()[param]
        return OAuth2WebServerFlow(
            client_info['client_id'], client_info['client_secret'],
            scope, **constructor_kwargs)
    except Exception as e:
        print "error", e


def resumable_upload(insert_request):
    """Start and check the uploaded request. """
    response = None
    error = None
    while response is None:
        try:
            print "Uploading file..."
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print "Video id '%s' was successfully uploaded." %response['id']
                    return response['id']
            else:
                exit("The upload failed with an unexpected response: %s" % response)
        except HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise


def initialize_upload(youtube, options):
    """Initilize the upload video."""
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category),
        status=dict(
            privacyStatus=options.privacyStatus))

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True))

    return resumable_upload(insert_request)


def get_args(name, path):
    """Create arguments to passed to the ."""
    args = Namespace(
        auth_host_name='localhost',
        auth_host_port=[8080, 8000],
        category='22',
        description='Test Description',
        file=path,
        keywords='',
        logging_level='ERROR',
        noauth_local_webserver=True,
        privacyStatus='public',
        title=name)

    return args


def get_authenticated_service():
    """Get youtube crecentials identified. """
    try:
        youtube_uploader = settings.YOUTUBE_UPLOADER
    except Exception as e:
        raise ValueError(e)
        pass

    scope = youtube_uploader['scope']
    credentials_path = youtube_uploader['credentials_path']
    client_info = youtube_uploader['client_info']
    credentials_file = youtube_uploader['credentials_file']

    my_flow_from_clientsecrets(client_info, scope)
    module_dir = os.path.abspath(credentials_path)
    file_path = os.path.join(module_dir, credentials_file)
    storage = Storage(file_path)
    credentials = storage.get()

    try:
        builded = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
            http=credentials.authorize(httplib2.Http()))
        return builded
    except Exception as e:
        print "error", e

