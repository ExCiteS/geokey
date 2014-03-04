from model_utils import Choices

STATUS = Choices('active', 'inactive')
FIELD_TYPES = {
    'TEXT': {
        'type_id': 0,
        'name': 'Text',
        'model': 'TextField'
    },
    'NUMBER': {
        'type_id': 1,
        'name': 'Numeric',
        'model': 'NumericField'
    },
    'TRUEFALSE': {
        'type_id': 2,
        'name': 'True/False',
        'model': 'TrueFalseField'
    },
    'LOOKUP': {
        'type_id': 3,
        'name': 'Lookup',
        'model': 'LookupField'
    },
    'DATETIME': {
        'type_id': 4,
        'name': 'Date and Time',
        'model': 'DateTimeField'
    }
}
