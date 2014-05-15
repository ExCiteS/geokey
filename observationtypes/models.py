import json

from iso8601 import parse_date
from iso8601.iso8601 import ParseError

from django.db import models
from django.db.models.loading import get_model
from django.db.models import Q

from core.exceptions import InputError

from .manager import ObservationTypeManager, FieldManager, LookupValueManager
from .base import STATUS


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

    class Meta:
        unique_together = ('key', 'observationtype')

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

    @classmethod
    def get_field_types(cls):
        return cls.__subclasses__()

    def validate_input(self, value):
        """
        Validates the given `value` against the field definition.
        @abstractmethod
        """
        raise NotImplementedError(
            'The method `validate_input` has not been implemented for this '
            'child class of Field.'
        )

    def validate_required(self, value):
        if self.required and (value is None):
            raise InputError('The field %s is required.' % self.name)

    def convert_from_string(self, value):
        """
        Converts the given `value` of an `Observation`'s field from `String`
        to the proper data type. By default returns simply the value in
        `String` format. Needs to be overridden in order to support other data
        types.
        """
        return value

    @property
    def fieldtype(self):
        return self.__class__.__name__

    @property
    def type_name(self):
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of Field.'
        )

    def filter(self, item, reference):
        raise NotImplementedError(
            'The method `filter` has not been implemented for this '
            'subclass of Field.'
        )


class TextField(Field):
    """
    A field for character strings.
    """

    def validate_required(self, value):
        if self.required and (value is None or len(value) == 0):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Validates if the given value is a valid input for the `TextField` by
        checking if the provided value is of type `String`.
        Returns `True` or `False`.
        """
        self.validate_required(value)

    @property
    def type_name(self):
        return 'Text'

    def filter(self, item, reference):
        return reference.lower() in item.attributes[self.key].lower()

    def get_filter(self, rule):
        return Q(attributes__icontains=rule)


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
        self.validate_required(value)

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

    @property
    def type_name(self):
        return 'Numeric'

    def filter(self, item, reference):
        value = json.loads(item.attributes[self.key])
        minval = reference.get('minval')
        maxval = reference.get('maxval')

        if minval is not None and maxval is not None:
            return value > minval and value < maxval
        else:
            if minval is not None:
                return value > minval

            if maxval is not None:
                return value < maxval

    def get_filter(self, rule):
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return (Q(attributes__gt={self.key: minval}) &
                    Q(attributes__lt={self.key: maxval}))
        else:
            if minval is not None:
                return Q(attributes__gt={self.key: minval})

            if maxval is not None:
                return Q(attributes__lt={self.key: maxval})


class TrueFalseField(Field):
    """
    A field that can only have two states True and False.
    """

    def validate_input(self, value):
        """
        Checks if the provided value is one of `True` or `False`
        Returns `True` or `False`.
        """
        self.validate_required(value)

        if value is not None and value not in [True, False]:
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

    @property
    def type_name(self):
        return 'True/False'

    def filter(self, item, reference):
        return reference == json.loads(item.attributes[self.key])

    def get_filter(self, rule):
        return Q(attributes__contains={self.key: json.dumps(rule)})


class DateTimeField(Field):
    """
    A field for storing dates and times.
    """

    def validate_required(self, value):
        if self.required and (value is None or len(value) == 0):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Checks if the provided value is a valid and ISO8601 compliant date
        string.
        """
        self.validate_required(value)

        try:
            parse_date(value)
        except ParseError:
            raise InputError('The value for DateTimeField %s is not a valid '
                             'date.' % self.name)

    @property
    def type_name(self):
        return 'Date and Time'

    def filter(self, item, reference):
        value = parse_date(item.attributes[self.key])
        minval = reference.get('minval')
        maxval = reference.get('maxval')

        if minval is not None and maxval is not None:
            return value > parse_date(minval) and value < parse_date(maxval)
        else:
            if minval is not None:
                return value > parse_date(minval)

            if maxval is not None:
                return value > parse_date(maxval)

    def get_filter(self, rule):
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return (Q(attributes__gt={self.key: minval}) &
                    Q(attributes__lt={self.key: maxval}))
        else:
            if minval is not None:
                return Q(attributes__gt={self.key: minval})

            if maxval is not None:
                return Q(attributes__lt={self.key: maxval})


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
        self.validate_required(value)

        valid = False
        for lookupvalue in self.lookupvalues.all():
            if lookupvalue.id == value:
                valid = True

        if not valid:
            raise InputError('The value for lookup field %s is not an '
                             'accepted value for the field.' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `int` format.
        """
        return int(value)

    @property
    def type_name(self):
        return 'Lookup'

    def filter(self, item, reference):
        return json.loads(item.attributes[self.key]) in reference

    def get_filter(self, rule):
        return Q(attributes__contains={self.key: rule})


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
