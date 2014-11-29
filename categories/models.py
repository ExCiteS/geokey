import json

from iso8601 import parse_date
from iso8601.iso8601 import ParseError

from django.conf import settings
from django.db import models
from django.db.models.loading import get_model

from core.exceptions import InputError

from .manager import CategoryManager, FieldManager, LookupValueManager
from .base import STATUS, DEFAULT_STATUS


class Category(models.Model):
    """
    Defines the data structure of a certain type of features.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey('projects.Project', related_name='categories')
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    default_status = models.CharField(
        choices=DEFAULT_STATUS,
        default=DEFAULT_STATUS.pending,
        max_length=20
    )
    colour = models.TextField(default='#0033ff')
    symbol = models.ImageField(upload_to='symbols', null=True)

    objects = CategoryManager()

    def re_order_fields(self, order):
        """
        Reorders the category fields according to the order given in `order`
        """
        fields_to_save = []
        for idx, field_id in enumerate(order):
            field = self.fields.get(pk=field_id)
            field.order = idx
            fields_to_save.append(field)

        for field in fields_to_save:
            field.save()

    def delete(self):
        self.status = STATUS.deleted
        self.save()


class Field(models.Model):
    """
    A Field defines data type of one characterictic of an obesrvation. Used to
    create forms of user interfaces and to validate user inputs.
    """
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=103)
    description = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)
    category = models.ForeignKey('Category', related_name='fields')
    order = models.IntegerField(default=0)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = FieldManager()

    class Meta:
        unique_together = ('key', 'category')

    @classmethod
    def create(self, name, key, description, required, category,
               field_type):
        """
        Creates a new field based on the field type provided.
        """
        model_class = get_model('categories', field_type)
        order = category.fields.count()

        field = model_class.objects.create(
            name=name,
            key=key,
            description=description,
            required=required,
            category=category,
            order=order
        )
        field.save()
        return field

    @classmethod
    def get_field_types(cls):
        """
        Returns a list of all available field types. Simply returns the names
        of the subclasses of `Field`
        """
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
        """
        Validates input value against required status. Raises an `InputError`
        if no value has been provided.
        """
        if self.status == STATUS.active and self.required and (value is None):
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
        """
        Returns the class name of the field instance
        """
        return self.__class__.__name__

    @property
    def type_name(self):
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of Field.'
        )

    def get_filter(self, item, reference):
        raise NotImplementedError(
            'The method `filter` has not been implemented for this '
            'subclass of Field.'
        )


class TextField(Field):
    """
    A field for character strings.
    """

    def validate_required(self, value):
        """
        Validate teh given value agaist required status. Checks if value is
        not None and has at least one character.
        """
        if self.status == STATUS.active and self.required and (
                value is None or len(str(value)) == 0):
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
        """
        Returns a human readable name of the field.
        """
        return 'Text'

    def get_filter(self, rule):
        """
        Returns the filter object for the given field based on the rule. Used
        to filter data for a view.
        """
        return '((attributes -> \'' + self.key + '\') \
            ILIKE \'%%' + rule + '%%\')'


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
        if isinstance(value, (str, unicode)) and len(value) == 0:
            value = None

        self.validate_required(value)

        if value is not None:
            if isinstance(value, (str, unicode)):
                try:
                    value = float(value) if '.' in value else int(value)
                except ValueError:
                    raise InputError(
                        'The value provided for field %s is not a number.' %
                        self.name
                    )

            if isinstance(value, (int, long, float, complex)):
                if self.minval and self.maxval and (
                        not (value >= self.minval) and (value <= self.maxval)):
                    raise InputError('The value provided for field %s must be '
                                     ' greater than %s and lower than %s.'
                                     % (self.name, self.minval, self.maxval))

                else:
                    if self.minval and (not (value >= self.minval)):
                        raise InputError('The value provided for field %s must'
                                         ' be greater than %s.'
                                         % (self.name, self.minval))

                    if self.maxval and (not (value <= self.maxval)):
                        raise InputError('The value provided for field %s must'
                                         ' be lower than %s.'
                                         % (self.name, self.maxval))

            else:
                raise InputError('The value provided for field %s is not a '
                                 'number.' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `Float` format.
        """
        if len(value) == 0:
            return None

        try:
            return int(value)
        except ValueError:
            return float(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.
        """
        return 'Numeric'

    def get_filter(self, rule):
        """
        Returns the filter object for the given field based on the rule. Used
        to filter data for a view.
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:

            return '(cast(attributes -> \'' + self.key + '\' as double \
                precision) >= ' + str(minval) + ') AND (cast(attributes \
                -> \'' + self.key + '\' as double precision) <= \
                ' + str(maxval) + ')'
        else:
            if minval is not None:
                return '(cast(attributes -> \'' + self.key + '\' as double \
                    precision) >= ' + str(minval) + ')'

            if maxval is not None:
                return '(cast(attributes -> \'' + self.key + '\' as double \
                    precision) <= ' + str(maxval) + ')'


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
        if value is not None:
            try:
                parse_date(value)
            except ParseError:
                raise InputError('The value for DateTimeField %s is not a '
                                 'valid date.' % self.name)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.
        """
        return 'Date and Time'

    def get_filter(self, rule):
        """
        Returns the filter object for the given field based on the rule. Used
        to filter data for a view.
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return '(to_date(attributes -> \'' + self.key + '\', \'YYYY-MM-DD \
                HH24:MI\') >= to_date(\'' + minval + '\', \'YYYY-MM-DD \
                HH24:MI\')) AND (to_date(attributes -> \'' + self.key + '\', \'\
                YYYY-MM-DD HH24:MI\') <= to_date(\'' + maxval + '\', \'\
                YYYY-MM-DD HH24:MI\'))'
        else:
            if minval is not None:
                return '(to_date(attributes -> \'' + self.key + '\', \'\
                    YYYY-MM-DD HH24:MI\') >= to_date(\'' + minval + '\', \'\
                    YYYY-MM-DD HH24:MI\'))'

            if maxval is not None:
                return '(to_date(attributes -> \'' + self.key + '\', \'\
                    YYYY-MM-DD HH24:MI\') <= to_date(\'' + maxval + '\', \'\
                    YYYY-MM-DD HH24:MI\'))'


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

        if value is not None:
            try:
                value = int(value)
            except ValueError:
                pass

            for lookupvalue in self.lookupvalues.all():
                if lookupvalue.id == value:
                    valid = True
        else:
            valid = True

        if not valid:
            raise InputError('The value for lookup field %s is not an '
                             'accepted value for the field.' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field in `int` format.
        """
        if value is None or len(value) == 0:
            return None

        return int(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.
        """
        return 'Select box'

    def get_filter(self, rule):
        """
        Returns the filter object for the given field based on the rule. Used
        to filter data for a view.
        """
        return '((attributes -> \'' + self.key + '\')::int IN \
            (' + ','.join(str(x) for x in rule) + '))'


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

    class Meta:
        ordering = ['id']

    def delete(self):
        """
        Deletes the value by settings its status to `deleted`
        """
        self.status = STATUS.inactive
        self.save()


class MultipleLookupField(Field):
    def validate_input(self, provided_vals):
        self.validate_required(provided_vals)

        valid = True

        if provided_vals is not None:
            if isinstance(provided_vals, (str, unicode)):
                provided_vals = json.loads(provided_vals)

            accepted_values = [value.id for value in self.lookupvalues.all()]
            intersection = [
                val for val in provided_vals if val in accepted_values
            ]

            valid = len(intersection) == len(provided_vals)

        if not valid:
            raise InputError('One or more values for the multiple select '
                             'field %s is not an accepted value for the '
                             'field.' % self.name)

    def convert_from_string(self, value):
        if value is None or len(value) == 0:
            return None

        return json.loads(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.
        """
        return 'Multiple select'

    def get_filter(self, rule):
        return '(regexp_split_to_array(\
            btrim(attributes -> \'' + self.key + '\', \'[]\'), \',\')::int[]\
            && ARRAY' + json.dumps(rule) + ')'


class MultipleLookupValue(models.Model):
    """
    Stores a single lookup value.
    """
    name = models.CharField(max_length=100)
    field = models.ForeignKey(MultipleLookupField, related_name='lookupvalues')
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )

    objects = LookupValueManager()

    class Meta:
        ordering = ['id']

    def delete(self):
        """
        Deletes the value by settings its status to `deleted`
        """
        self.status = STATUS.inactive
        self.save()
