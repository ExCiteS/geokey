"""Base for categories."""

from model_utils import Choices


STATUS = Choices('active', 'inactive')
FREQUENCY = Choices(
    '5min',
    '10min',
    '20min',
    '30min',
    'weekly',
    'monthly',
    'daily',
    'forthnightly',
    'hourly'
)
