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
    'UserGroup': [
        'name',
    ],
    'TextField': [
        'name',
        'status',
        'required',
    ],
    'NumericField': [
        'name',
        'status',
        'required',
    ],
    'DateTimeField': [
        'name',
        'status',
        'required',
    ],
    'DateField': [
        'name',
        'status',
        'required',
    ],
    'TimeField': [
        'name',
        'status',
        'required',
    ],
    'LookupField': [
        'name',
        'status',
        'required',
    ],
    'MultipleLookupField': [
        'name',
        'status',
        'required',
    ],
    'Location': [
        'name',
    ],
    'Subset': [
        'name',
        'can_contribute',
        'can_moderate',
    ],
}
