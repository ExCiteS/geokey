"""Test all utils."""

from django.test import TestCase

from oauth2client.client import OAuth2WebServerFlow

from geokey.contributions.utils import (
    my_flow_from_clientsecrets,
    get_args,
    get_authenticated_service,
    initialize_upload
)


class GetArgsTest(TestCase):
    """Test for method 'get_args'."""

    def setUp(self):
        """Set up tests."""
        self.path = 'path/sample/test/test_file.mp4'
        self.name = 'test_file'

    def test_method(self):
        """Test method."""
        args = get_args(self.name, self.path)
        args_var = vars(args)

        self.assertEqual(args_var['file'], self.path)

        self.assertEqual(args_var['title'], self.name)


class MyFlowFromClientSecretTest(TestCase):
    """Test for method 'my_flow_from_clientsecrets'."""

    def setUp(self):
        """Set up tests."""
        self.youtube_uploader = {
            'scope': "https://www.googleapis.com/auth/youtube.upload",
            'auth_host_name': 'localhost',
            'auth_host_port': [8080, 8000],
            'client_info': {
                "client_id": "109430273076-t3e30ie5aseb3laj2da0gkpikir6b0e9.apps.googleusercontent.com",
                "client_secret": "o3U69gnO4FRipA1Q3K6gi0_N",
                "redirect_uris": ["http://localhost"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            },

        }

    def test_method(self):
        """Test method."""
        flow = my_flow_from_clientsecrets(
            self.youtube_uploader['client_info'],
            self.youtube_uploader['scope'])

        client_info = self.youtube_uploader['client_info']

        constructor_kwargs = {
            'redirect_uri': None,
            'auth_uri': client_info['auth_uri'],
            'token_uri': client_info['token_uri'],
            'login_hint': None,
        }
        flow_new = OAuth2WebServerFlow(
            client_info['client_id'], client_info['client_secret'],
            self.youtube_uploader['scope'], **constructor_kwargs)
        self.assertEqual(flow.client_id, flow_new.client_id)
        self.assertEqual(flow.scope, flow_new.scope)
        self.assertEqual(flow.client_secret, flow_new.client_secret)
