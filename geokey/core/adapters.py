"""Core adapters."""

import re

from django.core.urlresolvers import reverse
from django.contrib import messages

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress


class AccountAdapter(DefaultAccountAdapter):
    """Adapter for accounts."""

    username_regex = re.compile(r'^.+$')

    def respond_user_inactive(self, request, user):
        """Resend email confirmation instructions if user is inactive."""
        try:
            email_address = EmailAddress.objects.get(
                user=user,
                email=user.email)
            self.add_message(
                request,
                messages.INFO,
                'account/messages/'
                'email_confirmation_sent.txt',
                {'email': user.email})
            email_address.send_confirmation(request)
        except EmailAddress.DoesNotExist:
            pass

        return super(AccountAdapter, self).respond_user_inactive(request, user)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter for social accounts."""

    def get_connect_redirect_url(self, request, socialaccount):
        """Return URL after successfull connecting a social account."""
        assert request.user.is_authenticated()
        url = reverse('admin:userprofile')
        return url
