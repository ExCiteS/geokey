"""Base for categories."""

from model_utils import Choices


STATUS = Choices('active', 'inactive')
FREQUENCY = Choices('weekly', 'monthly', 'daily', 'forthnightly', 'hourly')
