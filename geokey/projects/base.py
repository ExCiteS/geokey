"""Base for projects."""

from model_utils import Choices

from django.conf import settings


STATUS = Choices('active', 'inactive', 'deleted')
EVERYONE_CONTRIBUTES = Choices(*settings.ALLOWED_CONTRIBUTORS)
