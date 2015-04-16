import json

import time
from iso8601 import parse_date
from iso8601.iso8601 import ParseError

from django.conf import settings
from django.db import models
from django.db.models.loading import get_model

from geokey.core.exceptions import InputError
from geokey.datagroupings.models import Rule

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
    order = models.IntegerField(default=0)
    status = models.CharField(
        choices=STATUS,
        default=STATUS.active,
        max_length=20
    )
    display_field = models.ForeignKey(
        'categories.Field',
        null=True,
        related_name='display_field_of'
    )
    default_status = models.CharField(
        choices=DEFAULT_STATUS,
        default=DEFAULT_STATUS.pending,
        max_length=20
    )
    colour = models.TextField(default='#0033ff')
    symbol = models.ImageField(upload_to='symbols', null=True)

    objects = CategoryManager()

    class Meta:
        ordering = ['order']

    def re_order_fields(self, order):
        """
        Changes the order in which fields are displayed on client side.

        Parameters
        -------
        order : List
            IDs of fields, ordered according to new display order
        """
        fields_to_save = []
        for idx, field_id in enumerate(order):
            field = self.fields.get(pk=field_id)
            field.order = idx
            fields_to_save.append(field)

        for field in fields_to_save:
            field.save()

    def delete(self):
        """
        Deletes the category by setting its status to deleted.

        Notes
        -----
        It also deletes all contributions of that category and the rules for
        any data grouping of that category.
        """
        from geokey.contributions.models import Observation
        Observation.objects.filter(category=self).delete()
        Rule.objects.filter(category=self).delete()
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
    def create(self, name, key, description, required, category, field_type):
        """
        Creates a new field based on the field type provided.

        Parameters
        ----------
        name : str
            Name of the field. Used for displaying labels.
        key : str
            Key of the field. Used in API to assign values to a field.
        description : str
            Long description providing further details about the field.
        required : Boolean
            Indicates if the field is required
        category : geokey.categories.models.Category
            The category this field is assigned to.
        field_type : str
            Type of the field. Must be one of:
                - TextField
                - NumericField
                - DateField
                - DateTimeField
                - TimeField
                - LookupField
                - MultipleLookupfield

        Returns
        -------
        geokey.categories.models.Field
            Intance of the newly created field
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

        if order == 0:
            category.display_field = field
            category.save()

        return field

    @classmethod
    def get_field_types(cls):
        """
        Returns the names of the subclasses of Field.

        Returns
        -------
        List
            The names of available field types.
        """
        return cls.__subclasses__()

    def validate_input(self, value):
        """
        Validates the given value against the field definition.
        @abstractmethod
        """
        raise NotImplementedError(
            'The method `validate_input` has not been implemented for this '
            'child class of Field.'
        )

    def validate_required(self, value):
        """
        Validates input value against required status.
        Raises an `InputError` if no value has been provided.
        """
        if self.status == STATUS.active and self.required and (value is None):
            raise InputError('The field %s is required.' % self.name)

    def convert_from_string(self, value):
        """
        Converts the given value of an Observation's field from String
        to the proper data type. By default returns simply the value in
        String format. Needs to be overridden in order to support other data
        types.

        Notes
        -----
        Deprecated from version 0.6 on.
        """
        return value

    @property
    def fieldtype(self):
        """
        Returns the class name of the field instance

        Returns
        -------
        str
            The class name of the field instance
        """
        return self.__class__.__name__

    @property
    def type_name(self):
        """
        Returns the type name of the field instance. This is a human-readable
        name that can be used in user interfaces, e.g. Date and Time for
        DateTimeField.
        @abstractmethod
        """
        raise NotImplementedError(
            'The property `type_name` has not been implemented for this '
            'subclass of Field.'
        )

    def get_filter(self, rule):
        """
        Returns an SQL where clause that can be used to filter contributions in
        data groupings
        @abstractmethod

        Parameter
        ---------
        rule : str or list or dict
            Depending on the field type, this provides the values the filter
            should be built against

        Return
        ------
        str
            The where-clause that can be used in SQL queries.
        """
        raise NotImplementedError(
            'The method `filter` has not been implemented for this '
            'subclass of Field.'
        )

    def delete(self):
        """
        Deletes the field.

        Notes
        -----
        Also deletes all references to the Field in Rules.
        """
        rules = Rule.objects.filter(category=self.category)

        for rule in rules:
            rule.constraints.pop(self.key, None)
            rule.save()

        super(Field, self).delete()


class TextField(Field):
    """
    A field for character strings.
    """
    textarea = models.BooleanField(default=False)
    maxlength = models.IntegerField(blank=True, null=True)

    def validate_required(self, value):
        """
        Validate the given value agaist required status. Checks if value is
        not None and has at least one character.

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if no value is provided
        """
        if isinstance(value, str) or isinstance(value, unicode):
            value = value.encode('utf-8')

        if self.status == STATUS.active and self.required and (
                value is None or len(str(value)) == 0):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Validates if the given value is a valid input for the TextField.
        Checks if the value is required and if maxlength constraint is met.

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
        self.validate_required(value)

        if value is not None:
            if self.maxlength is not None and len(value) > self.maxlength:
                raise InputError('The input provided for text field %s '
                                 'contains too many characters.' % self.name)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Text'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : str
            A keyword that needs to matched for the filter to apply.

        Return
        ------
        str
            SQL where-clause
        """
        return ('((properties ->> \'' + self.key + '\') '
                'ILIKE \'%%' + rule + '%%\')')


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
        maxval.

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
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

    def convert_from_string(self, value):
        """
        Returns the `value` of the field either as float or int.

        Parameters
        ----------
        value : str
            The value to be converted

        Return
        ------
        int or float
            Value of the field

        Notes
        -----
        Deprecated from version 0.6 on.
        """
        if value is None or len(value) == 0:
            return None

        try:
            return int(value)
        except ValueError:
            return float(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Numeric'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : dict
            Contains either minimum and maximum value for the filer:
            {minval: 1, maxval: 10}

        Return
        ------
        str
            SQL where-clause
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return ('(cast(properties ->> \'%s\' as double precision) >= %s) '
                    'AND (cast(properties ->> \'%s\' as double precision) <= '
                    '%s)' % (self.key, minval, self.key, maxval))
        else:
            if minval is not None:
                return ('(cast(properties ->> \'%s\' as double '
                        'precision) >= %s)' % (self.key, minval))

            if maxval is not None:
                return ('(cast(properties ->> \'%s\' as double '
                        'precision) <= %s)' % (self.key,  maxval))


class DateTimeField(Field):
    """
    A field for storing dates and times.
    """

    def validate_required(self, value):
        """
        Validate the given value agaist required status. Checks if value is
        not None and has at least one character.

        Parameters
        ----------
        value : str or None
            The value to be validated

        Notes
        -----
        Raises InputError if no value is provided
        """
        if (self.status == STATUS.active and
                self.required and (value is None or len(value) == 0)):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Checks if the provided value is a valid and ISO8601 compliant date
        string.

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
        self.validate_required(value)
        if value is not None:
            try:
                parse_date(value)
            except ParseError:
                raise InputError('The value for DateField %s is not a '
                                 'valid date.' % self.name)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Date and Time'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : dict
            Contains either minimum and maximum value for the filer:
            {minval: '2015-10-01', maxval: '2015-10-31'}

        Return
        ------
        str
            SQL where-clause
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD HH24:MI\') '
                    '>= to_date(\'%s\', \'YYYY-MM-DD HH24:MI\')) AND '
                    '(to_date(properties ->> \'%s\', \'YYYY-MM-DD HH24:MI\') '
                    '<= to_date(\'%s\', \'YYYY-MM-DD HH24:MI\'))' %
                    (self.key, minval, self.key, maxval))
        else:
            if minval is not None:
                return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD '
                        'HH24:MI\') >= to_date(\'%s\', \'YYYY-MM-DD HH24:MI\''
                        '))' % (self.key, minval))

            if maxval is not None:
                return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD '
                        'HH24:MI\') <= to_date(\'%s\', \'YYYY-MM-DD HH24:MI\''
                        '))' % (self.key, maxval))


class DateField(Field):
    """
    A field for storing dates.
    """
    def validate_required(self, value):
        """
        Validate the given value agaist required status. Checks if value is
        not None and has at least one character.

        Parameters
        ----------
        value : str or None
            The value to be validated

        Notes
        -----
        Raises InputError if no value is provided
        """
        if (self.status == STATUS.active and self.required and
                (value is None or len(value) == 0)):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Checks if the provided value is a valid and ISO8601 compliant date
        string.

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
        self.validate_required(value)
        if value is not None:
            try:
                parse_date(value)
            except ParseError:
                raise InputError('The value for DateField %s is not a '
                                 'valid date.' % self.name)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Date'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : dict
            Contains either minimum and maximum value for the filer:
            {minval: '2015-10-01 10:00', maxval: '2015-10-31 15:00'}

        Return
        ------
        str
            SQL where-clause
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD\') '
                    '>= to_date(\'%s\', \'YYYY-MM-DD\')) AND '
                    '(to_date(properties ->> \'%s\', \'YYYY-MM-DD\') '
                    '<= to_date(\'%s\', \'YYYY-MM-DD\'))' %
                    (self.key, minval, self.key, maxval))
        else:
            if minval is not None:
                return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD'
                        '\') >= to_date(\'%s\', \'YYYY-MM-DD\''
                        '))' % (self.key, minval))

            if maxval is not None:
                return ('(to_date(properties ->> \'%s\', \'YYYY-MM-DD'
                        '\') <= to_date(\'%s\', \'YYYY-MM-DD\''
                        '))' % (self.key, maxval))


class TimeField(Field):
    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Time'

    def validate_required(self, value):
        """
        Validate the given value agaist required status. Checks if value is
        not None and has at least one character.

        Parameters
        ----------
        value : str or None
            The value to be validated

        Notes
        -----
        Raises InputError if no value is provided
        """
        if (self.status == STATUS.active and self.required and
                (value is None or len(value) == 0)):
            raise InputError('The field %s is required.' % self.name)

    def validate_input(self, value):
        """
        Checks if the provided value is a matches the patterns HH:mm

        Parameters
        ----------
        value : str
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
        self.validate_required(value)
        if value is not None:
            try:
                time.strptime(value, '%H:%M')
            except ValueError:
                raise InputError('The value for TimeField %s is not a '
                                 'valid time.' % self.name)

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : dict
            Contains either minimum and maximum value for the filer:
            {minval: '10:00', maxval: '15:00'}

        Return
        ------
        str
            SQL where-clause
        """
        minval = rule.get('minval')
        maxval = rule.get('maxval')

        if minval is not None and maxval is not None:
            if time.strptime(minval, '%H:%M') > time.strptime(maxval, '%H:%M'):
                return ('((properties ->> \'%s\')::time >= \'%s\'::time) OR '
                        '((properties ->> \'%s\')::time <= \'%s\'::time)' %
                        (self.key, minval, self.key, maxval))
            else:
                return ('((properties ->> \'%s\')::time >= \'%s\'::time) AND '
                        '((properties ->> \'%s\')::time <= \'%s\'::time)' %
                        (self.key, minval, self.key, maxval))
        else:
            if minval is not None:
                return ('((properties ->> \'%s\')::time >= \'%s\'::time)' %
                        (self.key, minval))

            if maxval is not None:
                return ('((properties ->> \'%s\')::time <= \'%s\'::time)' %
                        (self.key, maxval))


class LookupField(Field):
    """
    A lookup value is a special kind of field the provides an pre-defined
    number of values as valid input values.
    """
    def validate_input(self, value):
        """
        Checks if the provided value matches the ID of one of the field's
        lookupvalues.

        Parameters
        ----------
        value : int
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
        self.validate_required(value)

        valid = False

        if value is not None:
            try:
                value = int(value)
                for lookupvalue in self.lookupvalues.all():
                    if lookupvalue.id == value:
                        valid = True
            except ValueError:
                pass
        else:
            valid = True

        if not valid:
            raise InputError('The value for lookup field %s is not an '
                             'accepted value for the field.' % self.name)

    def convert_from_string(self, value):
        """
        Returns the `value` of the field int.

        Parameters
        ----------
        value : str
            The value to be converted

        Return
        ------
        int
            Value of the field

        Notes
        -----
        Deprecated from version 0.6 on.
        """
        if value is None or len(value) == 0:
            return None

        return int(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Select box'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : List
            IDs of LookupValues that need to matched in order for the filter
            to apply.

        Return
        ------
        str
            SQL where-clause
        """
        return ('((properties ->> \'%s\')::int IN (%s))' %
                (self.key, ','.join(str(x) for x in rule)))


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
        """
        Checks if the provided value matches the ID of one of the field's
        lookupvalues.

        Parameters
        ----------
        value : int
            The value to be validated

        Notes
        -----
        Raises InputError if an invalid value is provided
        """
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
        """
        Returns the `value` of the field as List.

        Parameters
        ----------
        value : str
            The value to be converted

        Return
        ------
        List
            List of lookup value IDs

        Notes
        -----
        Deprecated from version 0.6 on.
        """
        if value is None or len(value) == 0:
            return None

        return json.loads(value)

    @property
    def type_name(self):
        """
        Returns a human readable name of the field.

        Return
        ------
        str
            The name of the field
        """
        return 'Multiple select'

    def get_filter(self, rule):
        """
        Returns the SQL where clause for the given field based on the rule.
        Used to filter data for a data grouping.

        Parameter
        ---------
        rule : List
            IDs of LookupValues that need to matched in order for the filter
            to apply.

        Return
        ------
        str
            SQL where-clause
        """
        return ('(regexp_split_to_array(btrim(properties ->> \'%s\', \'[]\'),'
                ' \',\')::int[] && ARRAY%s)' % (self.key, json.dumps(rule)))


class MultipleLookupValue(models.Model):
    """
    Stores a multiple lookup value.
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
