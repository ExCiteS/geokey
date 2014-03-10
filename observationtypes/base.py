from model_utils import Choices

STATUS = Choices('active', 'inactive')
FIELD_TYPES = {
    'TextField': {
        'name': 'Text'
    },
    'NumericField': {
        'name': 'Numeric'
    },
    'TrueFalseField': {
        'name': 'True/False'
    },
    'LookupField': {
        'name': 'Lookup'
    },
    'DateTimeField': {
        'name': 'Date/Time'
    }
}
