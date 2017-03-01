"""Core base."""

from model_utils import Choices


STATUS_ACTION = Choices('created', 'updated', 'deleted')
LOG_MODELS = {
    'Project': [
        'name',
        'status',
        'isprivate',
        'islocked',
        'everyone_contributes',
        'geographic_extent',
    ],
    'Category': [
        'name',
        'status',
        'default_status',
    ],
}
