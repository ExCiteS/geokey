"""Base for projects."""

from model_utils import Choices

from django.conf import settings


STATUS = Choices('active', 'inactive', 'deleted')
allowed = ("auth", "false", "true")
if hasattr(settings, 'ALLOWED_CONTRIBUTORS'):
    allowed = settings.ALLOWED_CONTRIBUTORS
EVERYONE_CONTRIBUTES = Choices(*allowed)
