"""Base for logger."""

from model_utils import Choices


STATUS_ACTION = Choices('created', 'deleted', 'updated')


list_of_models = (
    'User',
    'Category',
    'Subset',
    'Project',
    'Observation',
    'Field',
    'Comment',
    'UserGroup',
    'TextField',
    'NumericField',
    'DateTimeField',
    'DateField',
    'TimeField',
    'LookupField',
    'MultipleLookupField',
    'Field'
)
#######

#######
actions_dic = {
    'User':
    {
        'display_name': 'User renamed'
    },

    'Comment':
    {
        'status': 'Comment deleted',
        'review_status': 'Comment review status to ',
    },
    'Observation':
    {
        # '_location_cache': 'Location has been changed',
        'status': 'Observation is '
    },
    'Field':
    {
        # '_location_cache': 'Location has been changed',
        'Required': 'Field is required'
    },
    'Subset':
    {
        'name': 'Subset renamed'
    },
    'TextField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'NumericField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'DateTimeField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'TimeField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'LookupField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'DateField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'MultipleLookupField':
    {
        'name': 'Field renamed',
        'status': 'Field is '
    },
    'UserGroup':
    {
        'name': 'User groups renamed',
        'can_moderate': 'User groups permissions changed'
    },
    'Category':
    {
        'name': 'Category renamed',
        'status': 'Category is ',
        'default_status': 'Category default status changed'
    },
    'Project':
    {
        'name': 'Project renamed',
        'geographic_extent' : 'Project geogr. ext. changed',
        'everyone_contributes': 'Project permissions changed',
        'isprivate': 'Project is ',
        'status': 'Project deleted'
    }
}
