"""Base for logger."""

from model_utils import Choices


STATUS_ACTION = Choices('created', 'deleted', 'updated')


list_of_models = (
    'Project',
    # 'UserGroup',
    'Category',
    # 'Field',
    # 'TextField',
    # 'NumericField',
    # 'DateTimeField',
    # 'DateField',
    # 'TimeField',
    # 'LookupField',
    # 'MultipleLookupField',
    # 'Observation',
    # 'Comment',
    # 'Subset',
)
#######

actions_dic = {
    'User':
    {
        'display_name': STATUS_ACTION.updated
    },

    'Comment':
    {
        'status': STATUS_ACTION.deleted,
        'review_status': STATUS_ACTION.updated,
    },
    'Observation':
    {
        # '_location_cache': 'Location has been changed',
        'status': STATUS_ACTION.updated,
    },
    'Field':
    {
        'Required': STATUS_ACTION.updated,
    },
    'Subset':
    {
        'name': STATUS_ACTION.updated,
    },
    'TextField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated,
    },
    'NumericField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated,
    },
    'DateTimeField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated
    },
    'TimeField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated
    },
    'LookupField':
    {
        'name': STATUS_ACTION.updated,
        'status': 'Field is '
    },
    'DateField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated
    },
    'MultipleLookupField':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated
    },
    'UserGroup':
    {
        'name': STATUS_ACTION.updated,
        'can_moderate': STATUS_ACTION.updated
    },
    'Category':
    {
        'name': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated,
        'default_status': STATUS_ACTION.updated
    },
    'Project':
    {
        'name': STATUS_ACTION.updated,
        'geographic_extent': STATUS_ACTION.updated,
        'everyone_contributes': STATUS_ACTION.updated,
        'isprivate': STATUS_ACTION.updated,
        'status': STATUS_ACTION.updated,
        'islocked': STATUS_ACTION.updated
    }
}
