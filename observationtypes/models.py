import iso8601

from django.db import models

from model_utils import Choices


STATUS = Choices('active', 'inactive')


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

    def update(self, name=None, description=None, status=None):
        if (name):
            self.name = name
        if (description):
            self.description = description
        if (status is not None):
            self.status = status

        self.save()


class Field(models.Model):
    """
    A Field defines data type of one characterictic of an obesrvation. Used to
    create forms of user interfaces and to validate user inputs.
    """
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=30)
    description = models.TextField()
    required = models.BooleanField(default=False)
    featuretype = models.ForeignKey('ObservationType')
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    def getInstance(self):
        """
        Returns the child instance of the fields. When getting all fields from
        a feature type only the parent field instances are return; i.e. fields
        and methods of child instances are not given.
        """
        try:
            return self.textfield
        except Field.DoesNotExist:
            pass
        try:
            return self.numericfield
        except Field.DoesNotExist:
            pass
        try:
            return self.truefalsefield
        except Field.DoesNotExist:
            pass
        try:
            return self.lookupfield
        except Field.DoesNotExist:
            pass
        try:
            return self.datetimefield
        except Field.DoesNotExist:
            pass

    def validateInput(self, value):
        """
        Validates the given `value` against the field definition.
        @abstractmethod
        """
        raise NotImplementedError(
            'The method `validateInput` has not been implemented for this '
            'child class of Field.'
        )

    def convertFromString(self, value):
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

    def validateInput(self, value):
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
    minval = models.FloatField(null=True)
    maxval = models.FloatField(null=True)

    def validateInput(self, value):
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

    def convertFromString(self, value):
        """
        Returns the `value` of the field in `Float` format.
        """
        return float(value)

    def update(
            self, name=None, description=None, status=None, required=None,
            minval=None, maxval=None):
        self.minval = minval
        self.maxval = maxval

        self.save()

        super(NumericField, self).update(
            name=name, description=description, status=status,
            required=required
        )


class TrueFalseField(Field):
    """
    A field that can only have two states True and False.
    """

    def validateInput(self, value):
        """
        Checks if the provided value is one of `True`, `False`, `'True'`,
        `'true'`, `'1'`, `'t'`, `'False'`, `'false'`, `'0'`, `'f'`, `0`, `1`.
        Returns `True` or `False`.
        """
        return value in [
            True, False, 'True', 'true', '1', 't', 'False', 'false', '0',
            'f', 0, 1
        ]

    def convertFromString(self, value):
        """
        Returns the `value` of the field in `Bool` format.
        """
        return value in [True, 'True', 'true', '1', 't', 1]


class DateTimeField(Field):
    """
    A field for storing dates and times.
    """

    def validateInput(self, value):
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
    def validateInput(self, value):
        """
        Checks if the provided value is in the list of `LookupValue`'s.
        Returns `True` or `False`.
        """
        valid = False
        for lookupvalue in self.lookupvalue_set:
            if lookupvalue.id == value:
                valid = True

        return valid

    def convertFromString(self, value):
        """
        Returns the `value` of the field in `int` format.
        """
        return int(value)


class LookupValue(models.Model):
    """
    Stores a single lookup value.
    """
    name = models.CharField(max_length=100)
    field = models.ForeignKey(LookupField)
    status = models.IntegerField(choices=STATUS, default=STATUS.active)

    def update(self, status=None):
        """
        Updates the status pf the lookup.
        """
        if status is not None:
            self.status = status
        self.save()
