"""Template tags for social features."""

from django import template

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp


register = template.Library()


@register.assignment_tag
def get_social_apps():
    """Get all enabled social apps."""
    social_apps = SocialApp.objects.filter(
        provider__in=[id for id, name in providers.registry.as_choices()]
    ).exclude(client_id__exact='').distinct()

    for social_app in social_apps:
        social_app.provider = providers.registry.by_id(social_app.provider)

    return social_apps
