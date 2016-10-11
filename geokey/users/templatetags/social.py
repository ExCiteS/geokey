"""Template tags for social features."""

from django import template
from django.db.models import Q

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp


register = template.Library()


@register.assignment_tag
def get_social_apps():
    """Get all enabled social apps."""
    social_apps = SocialApp.objects.exclude(Q(client_id__exact='')).distinct()

    for social_app in social_apps:
        try:
            provider = providers.registry.by_id(social_app.provider)
        except:
            provider = None

        social_app.provider = provider

    return social_apps
