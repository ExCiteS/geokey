"""Base for categories."""

from model_utils import Choices


STATUS = Choices('active', 'inactive', 'deleted')
DEFAULT_STATUS = Choices('active', 'pending')
