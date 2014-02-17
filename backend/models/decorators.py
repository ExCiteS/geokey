from django.core.exceptions import ValidationError

from .choice import STATUS_TYPES


def check_status(func):
    """
    A decorator used in update methods of model entities.
    """
    ACCEPTED_STATUS = (
        STATUS_TYPES['ACTIVE'],
        STATUS_TYPES['INACTIVE']
    )

    def wrapped(*args, **kwargs):
        status = kwargs.get('status')
        if ((status is None) or (status in ACCEPTED_STATUS)):
            return func(*args, **kwargs)
        else:
            raise ValidationError(
                'The status provided is invalid. Accepted values are ACTIVE'
                'or INACTIVE'
            )

    return wrapped
