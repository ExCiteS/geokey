"""Base for projects."""

from model_utils import Choices

from local_settings.settings import ALLOWED_CONTRIBUTORS


STATUS = Choices('active', 'inactive', 'deleted')
EVERYONE_CONTRIBUTES = Choices(*ALLOWED_CONTRIBUTORS)
