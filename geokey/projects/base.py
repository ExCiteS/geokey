"""Base for projects."""

from model_utils import Choices


STATUS = Choices('active', 'inactive', 'deleted')
EVERYONE_CONTRIBUTES = Choices('true', 'auth', 'false')
