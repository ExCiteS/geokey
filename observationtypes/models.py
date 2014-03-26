import iso8601

from django.db import models
from django.db.models.loading import get_model

from core.exceptions import InputError

from .manager import ObservationTypeManager, FieldManager, LookupValueManager
from .base import STATUS, FIELD_TYPES


class ObservationType(models.Model):
    """
    Defines the data structure of a certain type of features.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey(
        'projects.Project', related_name='observationtypes'
    )
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = ObservationTypeManager()


class Field(models.Model):
    """
    A Field defines data type of one characterictic of an obesrvation. Used to
    create forms of user interfaces and to validate user inputs.
    """
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=30)
    description = models.TextField()
    required = models.BooleanField(default=False)
    observationtype = models.ForeignKey(
        'ObservationType', related_name='fields'
    )
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = FieldManager()

    @classmethod
    def create(self, name, key, description, required, observation_type,
               field_type):
        model_class = get_model('observationtypes', field_type)
        field = model_class.objects.create(
            name=name,
            key=key,
            description=description,
            required=required,
            observationtype=observation_type,
        )
        field.save()
        return field

    def get_type_name(self):
        return FIELD_TYPES.get(self.__class__.__name__).get('name')

    def validate_input(self, value):
        """
        Validates the given `value` against the field definition.
        @abstractmethod
        """
        raise NotImplementedError(
            'The method `validate_input` has not been implemented for this '
            'child class of Field.'
        )

    def convert_from_string(self, value):
        """
        Converts the given `value` of an `Observation`'s field from `String`
        to the proper data type. By default returns simply the value in
        `String` format. Needs to be overridden in order to support other data
        types.
        """
        return value


class TextField(Field):
    """
    A field for character strings.
    """

    def validate_input(self, value):
        """
        Validates if the given value is a valid input for the `TextField` by
        checking if the provided value is of type `String`.
        Returns `True` or `False`.
        """
        if not isinstance(value, basestring):
            raise InputError('The input value for text field is not a valid '
                             'string.')


class NumericField(Field):
    """
    A field for numeric values.
    """
    minval = models.FloatField(blank=True, null=True)
    maxval = models.FloatField(blank=True, null=True)

    def validate_input(self, value):
        """
        Validates if the given value is a valid input for the NumerField.
        Checks if a value of type number has been provided or if a value of
        type String has been provided that can be successfully converted to a
        Float value. Then checks if the value is between bounds of minval and
        maxval. Returns `True` or `False`.
        """

        if isinstance(value, (int, long, float, complex)):
            if self.minval and self.maxval and (
                    not (value >= self.minval) and (value <= self.maxval)):
                raise InputError('The value provided for field %s must be '
                                 ' greater than %s and lower than %s.'
                                 % (self.name, self.minval, self.maxval))

            else:
                if self.minval and (not (value >= self.minval)):
                    raise InputError('The value provided for field %s must '
                                     'be greater than %s.'
                                     % (self.name, self.minval))

                if self.maxval and (not (value <= self.maxval)):
                    raise InputError('The value provided for field %s must '
                                     'be lower than %s.'
                                     % (self.name, self.maxval))

        else:
            raise InputError('The value provided for field %s is not a '
                             'number.' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `Float` format.
        """
        try:
            return int(value)
        except ValueError:
            return float(value)


class TrueFalseField(Field):
    """
    A field that can only have two states True and False.
    """

    def validate_input(self, value):
        """
        Checks if the provided value is one of `True` or `False`
        Returns `True` or `False`.
        """
        if value not in [True, False]:
            raise InputError('The value for TrueFalseField %s must be one of '
                             'True or False' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `Bool` format.
        """
        if value == 'True':
            return True
        else:
            return False


class DateTimeField(Field):
    """
    A field for storing dates and times.
    """

    def validate_input(self, value):
        """
        Checks if the provided value is a valid and ISO8601 compliant date
        string.
        """

        try:
            iso8601.parse_date(value)
        except iso8601.iso8601.ParseError:
            raise InputError('The value for DateTimeField %s is not a valid '
                             'date.' % self.name)


class LookupField(Field):
    """
    A lookup value is a special kind of field the provides an pre-defined
    number of values as valid input values.
    """
    def validate_input(self, value):
        """
        Checks if the provided value is in the list of `LookupValue`'s.
        Returns `True` or `False`.
        """
        valid = False
        for lookupvalue in self.lookupvalues.all():
            if lookupvalue.id == value:
                valid = True

        if not valid:
            raise InputError('The value for lookup field %s is not an '
                             'accepted value for the field' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `int` format.
        """
        return int(value)


class LookupValue(models.Model):
    """
    Stores a single lookup value.
    """
    name = models.CharField(max_length=100)
    field = models.ForeignKey(LookupField, related_name='lookupvalues')
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = LookupValueManager()

    def delete(self):
        self.status = STATUS.inactive
        self.save()
