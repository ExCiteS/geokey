import iso8601

from django.db import models
from django.db.models.loading import get_model

from .manager import ObservationTypeManager, FieldManager
from .base import STATUS, FIELD_TYPES


class ObservationType(models.Model):
    """
    Defines the data structure of a certain type of features.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    project = models.ForeignKey('projects.Project')
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
    observationtype = models.ForeignKey('ObservationType')
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
        return isinstance(value, basestring)


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
        valid = False

        if not isinstance(value, bool):
            try:
                value = float(value)
            except ValueError:
                pass

        valid = isinstance(value, float)

        if valid:
            if self.minval and self.maxval:
                valid = (value >= self.minval) and (value <= self.maxval)
            else:
                if self.minval:
                    valid = (value >= self.minval)
                if self.maxval:
                    valid = (value <= self.maxval)

        return valid

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `Float` format.
        """
        return float(value)


class TrueFalseField(Field):
    """
    A field that can only have two states True and False.
    """

    def validate_input(self, value):
        """
        Checks if the provided value is one of `True`, `False`, `'True'`,
        `'true'`, `'1'`, `'t'`, `'False'`, `'false'`, `'0'`, `'f'`, `0`, `1`.
        Returns `True` or `False`.
        """
        return value in [
            True, False, 'True', 'true', '1', 't', 'False', 'false', '0',
            'f', 0, 1
        ]

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `Bool` format.
        """
        return value in [True, 'True', 'true', '1', 't', 1]


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
            return True
        except iso8601.iso8601.ParseError:
            return False


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

        return valid

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

    def delete(self):
        self.status = STATUS.inactive
        self.save()
