import json
from django.test import TestCase

from nose.tools import raises

from geokey.core.exceptions import InputError

from ..models import Field, Category

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    LookupFieldFactory, LookupValueFactory, TimeFieldFactory,
    FieldFactory, CategoryFactory, MultipleLookupFieldFactory,
    MultipleLookupValueFactory, DateFieldFactory
)

from geokey.datagroupings.models import Rule
from geokey.datagroupings.tests.model_factories import GroupingFactory, RuleFactory
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.contributions.models import Observation


class CategoryTest(TestCase):
    def test_re_order_fields(self):
        category = CategoryFactory.create()

        field_0 = TextFieldFactory.create(**{'category': category})
        field_1 = TextFieldFactory.create(**{'category': category})
        field_2 = TextFieldFactory.create(**{'category': category})
        field_3 = TextFieldFactory.create(**{'category': category})
        field_4 = TextFieldFactory.create(**{'category': category})

        category.re_order_fields(
            [field_4.id, field_0.id, field_2.id, field_1.id,  field_3.id]
        )

        fields = category.fields.all()

        self.assertTrue(fields.ordered)
        self.assertEqual(fields[0], field_4)
        self.assertEqual(fields[1], field_0)
        self.assertEqual(fields[2], field_2)
        self.assertEqual(fields[3], field_1)
        self.assertEqual(fields[4], field_3)

    def test_re_order_fields_with_false_field(self):
        category = CategoryFactory.create()

        field_0 = TextFieldFactory.create(**{'category': category})
        field_1 = TextFieldFactory.create(**{'category': category})
        field_2 = TextFieldFactory.create(**{'category': category})
        field_3 = TextFieldFactory.create(**{'category': category})
        field_4 = TextFieldFactory.create(**{'category': category})

        try:
            category.re_order_fields(
                [field_4.id, field_0.id, field_2.id, field_1.id,  5854]
            )
        except Field.DoesNotExist:
            fields = category.fields.all()

            self.assertTrue(fields.ordered)
            self.assertEqual(fields[0].order, 0)
            self.assertEqual(fields[1].order, 0)
            self.assertEqual(fields[2].order, 0)
            self.assertEqual(fields[3].order, 0)
            self.assertEqual(fields[4].order, 0)

    @raises(Category.DoesNotExist)
    def test_delete(self):
        category = CategoryFactory.create()
        category.delete()
        Category.objects.get(pk=category.id)

    @raises(Category.DoesNotExist, Rule.DoesNotExist)
    def test_delete_with_grouping(self):
        category = CategoryFactory.create()

        grouping = GroupingFactory.create()
        rule = RuleFactory(**{
            'grouping': grouping,
            'status': 'active',
            'category': category
        })
        category.delete()

        Category.objects.get(pk=category.id)
        Rule.objects.get(pk=rule.id)

    @raises(Category.DoesNotExist, Observation.DoesNotExist)
    def test_delete_with_observation(self):
        category = CategoryFactory.create()
        observation = ObservationFactory.create(**{
            'category': category
        })
        category.delete()

        Category.objects.get(pk=category.id)
        Observation.objects.get(pk=observation.id)


class FieldTest(TestCase):
    @raises(NotImplementedError)
    def test_field_validate_input(self):
        field = FieldFactory()
        field.validate_input('Bla')

    @raises(NotImplementedError)
    def test_field_type_name(self):
        field = FieldFactory()
        field.type_name

    @raises(NotImplementedError)
    def test_field_get_filter(self):
        field = FieldFactory()
        field.get_filter('Bla')

    def test_get_field_types(self):
        field_types = Field.get_field_types()
        self.assertEqual(len(field_types), 7)

    def test_order(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'TextField'
        )
        self.assertEqual(field.order, 0)

        another_field = Field.create(
            'name-2', 'key-2', 'description', False, category,
            'TextField'
        )
        self.assertEqual(another_field.order, 1)

    @raises(Field.DoesNotExist)
    def test_delete(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'TextField'
        )

        f = Field.objects.get(pk=field.id)
        f.delete()

        Field.objects.get(pk=f.id)

    def test_delete_with_rule(self):
        category = CategoryFactory()
        Field.create(
            'n', 'n', 'n', False, category, 'TextField'
        )
        field = Field.create(
            'name', 'key', 'description', False, category, 'TextField'
        )
        grouping = GroupingFactory.create()
        rule = RuleFactory(**{
            'grouping': grouping,
            'status': 'active',
            'category': category,
            'constraints': {
                field.key: 'Blah',
                'other-key': 'blubb'
            }
        })
        field.delete()
        reference_rule = Rule.objects.get(pk=rule.id)
        self.assertEquals(reference_rule.constraints.get('key'), None)


class TextFieldTest(TestCase):
    def test_create_textfield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'TextField'
        )
        self.assertEqual(field.__class__.__name__, 'TextField')

    def test_get_name(self):
        field = TextFieldFactory()
        self.assertEqual(field.type_name, 'Text')
        self.assertEqual(field.fieldtype, 'TextField')

    def test_textfield_validate_input(self):
        textfield = TextFieldFactory()
        try:
            textfield.validate_input('Bla')
        except InputError:
            self.fail('TextField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_textfield_validate_input_maxlength(self):
        textfield = TextFieldFactory(**{'maxlength': 10})
        try:
            textfield.validate_input('BlaBlaBlaB')
        except InputError:
            self.fail('TextField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_textfield_validate_input_maxlength_too_long(self):
        textfield = TextFieldFactory(**{'maxlength': 10})
        textfield.validate_input('BlaBlaBlaBla')

    def test_textfield_validate_required(self):
        textfield = TextFieldFactory.create(**{'required': True})
        try:
            textfield.validate_input('Bla')
        except InputError:
            self.fail('TextField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_textfield_validate_required_empty_string(self):
        textfield = TextFieldFactory.create(**{'required': True})
        textfield.validate_input('')

    def test_textfield_validate_inactive_required_empty_string(self):
        textfield = TextFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            textfield.validate_input('')
        except InputError:
            self.fail('TextField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_textfield_validate_required_none_type(self):
        textfield = TextFieldFactory.create(**{'required': True})
        textfield.validate_input(None)

    def test_textfield_convert_from_String(self):
        textfield = TextFieldFactory()
        self.assertEqual('Bla', textfield.convert_from_string('Bla'))

    def test_get_filter(self):
        textfield = TextFieldFactory(**{'key': 'key'})
        self.assertEqual(
            textfield.get_filter('blah'),
            "((properties ->> 'key') ILIKE '%%blah%%')"
        )


class NumericFieldTest(TestCase):
    def test_create_numericfield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'NumericField'
        )
        self.assertEqual(field.__class__.__name__, 'NumericField')

    def test_get_name(self):
        field = NumericFieldFactory()
        self.assertEqual(field.type_name, 'Numeric')
        self.assertEqual(field.fieldtype, 'NumericField')

    def test_numericfield_validate_required(self):
        numericfield = NumericFieldFactory.create(**{'required': True})
        try:
            numericfield.validate_input(2)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_required_none_type(self):
        numericfield = NumericFieldFactory.create(**{'required': True})
        numericfield.validate_input(None)

    def test_numericfield_validate_not_required_none_type(self):
        numericfield = NumericFieldFactory.create(**{'required': False})
        try:
            numericfield.validate_input(None)
        except InputError:
            self.fail('numericfield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_numericfield_validate_inactive_required_empty_string(self):
        numericfield = NumericFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            numericfield.validate_input(None)
        except InputError:
            self.fail('numericfield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_numericfield_validate_input_number(self):
        numeric_field = NumericFieldFactory()
        try:
            numeric_field.validate_input(158)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_numericfield_validate_input_string_number(self):
        numeric_field = NumericFieldFactory()
        try:
            numeric_field.validate_input('12')
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_input_string_char(self):
        numeric_field = NumericFieldFactory()
        numeric_field.validate_input('bla')

    # @raises(InputError)
    def test_numericfield_validate_input_empty_string(self):
        numeric_field = NumericFieldFactory()
        numeric_field.validate_input('')

    def test_numericfield_validate_input_minval(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10
        })
        try:
            numeric_field.validate_input(12)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_input_too_small_minval(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10
        })
        numeric_field.validate_input(5)

    def test_numericfield_validate_input_maxval(self):
        numeric_field = NumericFieldFactory(**{
            'maxval': 20
        })
        try:
            numeric_field.validate_input(12)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_input_too_big_maxval(self):
        numeric_field = NumericFieldFactory(**{
            'maxval': 20
        })
        numeric_field.validate_input(21)
        self.assertTrue(numeric_field.validate_input(12))

    def test_numericfield_validate_input_minval_maxval(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10,
            'maxval': 20
        })
        try:
            numeric_field.validate_input(12)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_input_minval_maxval_too_small(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10,
            'maxval': 20
        })
        numeric_field.validate_input(5)

    @raises(InputError)
    def test_numericfield_validate_input_minval_maxval_too_big(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10,
            'maxval': 20
        })
        numeric_field.validate_input(21)

    def test_numericfield_convert_from_string(self):
        numeric_field = NumericFieldFactory()
        self.assertEqual(100, numeric_field.convert_from_string('100'))
        self.assertEqual(1.2, numeric_field.convert_from_string('1.2'))

    def test_numericfield_convert_from_empty_string(self):
        numeric_field = NumericFieldFactory()
        self.assertEqual(None, numeric_field.convert_from_string(''))

    def test_get_filter(self):
        numeric_field = NumericFieldFactory(**{'key': 'key'})
        self.assertEqual(
            numeric_field.get_filter({'minval': 10, 'maxval': 20}),
            "(cast(properties ->> 'key' as double precision) >= 10) AND "
            "(cast(properties ->> 'key' as double precision) <= 20)"
        )
        self.assertEqual(
            numeric_field.get_filter({'minval': 10}),
            "(cast(properties ->> 'key' as double precision) >= 10)"
        )
        self.assertEqual(
            numeric_field.get_filter({'maxval': 20}),
            "(cast(properties ->> 'key' as double precision) <= 20)"
        )


class SingleLookupFieldTest(TestCase):
    def test_create_lookupfield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'LookupField'
        )
        self.assertEqual(field.__class__.__name__, 'LookupField')

    def test_get_name(self):
        field = LookupFieldFactory()
        self.assertEqual(field.type_name, 'Select box')
        self.assertEqual(field.fieldtype, 'LookupField')

    def test_lookupfield_validate_required(self):
        lookup_field = LookupFieldFactory.create(**{'required': True})
        lookup_value = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_field.validate_input(lookup_value.id)

    @raises(InputError)
    def test_lookupfield_validate_required_none_type(self):
        lookup_field = LookupFieldFactory.create(**{'required': True})
        lookup_field.validate_input(None)

    def test_lookupfield_validate_not_required_none_type(self):
        lookup_field = LookupFieldFactory.create(**{'required': False})
        try:
            lookup_field.validate_input(None)
        except InputError:
            self.fail('lookup_field.validate_input() raised InputError '
                      'unexpectedly!')

    def test_lookupfield_validate_inactive_required_empty_string(self):
        lookup_field = LookupFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            lookup_field.validate_input(None)
        except InputError:
            self.fail('LookupField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_lookupfield_validate_input(self):
        lookup_field = LookupFieldFactory()
        lookup_value = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        try:
            lookup_field.validate_input(lookup_value.id)
        except InputError:
            self.fail('LookupField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_lookupfield_validate_wrong_input(self):
        lookup_field = LookupFieldFactory()
        LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_field.validate_input(781865458)

    @raises(InputError)
    def test_lookupfield_validate_wrong_input_string(self):
        lookup_field = LookupFieldFactory()
        LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        lookup_field.validate_input('blah')

    def test_lookupfield_convert_from_string(self):
        lookup_field = LookupFieldFactory()
        lookup_value = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        self.assertEqual(
            lookup_value.id,
            lookup_field.convert_from_string(str(lookup_value.id))
        )
        self.assertIsNone(lookup_field.convert_from_string(''))
        self.assertIsNone(lookup_field.convert_from_string(None))

    def test_get_filter(self):
        lookup_field = LookupFieldFactory(**{'key': 'key'})
        self.assertEqual(
            lookup_field.get_filter([1, 2, 3]),
            '((properties ->> \'key\')::int IN (1,2,3))'
        )


class DateTimeFieldTest(TestCase):
    def test_create_datetimefield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'DateTimeField'
        )
        self.assertEqual(field.__class__.__name__, 'DateTimeField')

    def test_get_name(self):
        field = DateTimeFieldFactory()
        self.assertEqual(field.type_name, 'Date and Time')
        self.assertEqual(field.fieldtype, 'DateTimeField')

    def test_datetimefield_validate_required(self):
        datetimefield = DateTimeFieldFactory.create(**{'required': True})
        try:
            datetimefield.validate_input('2014-01-01')
        except InputError:
            self.fail('datetimefield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_datetimefield_validate_inactive_required_empty_string(self):
        datetimefield = DateTimeFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            datetimefield.validate_input(None)
        except InputError:
            self.fail('datetimefield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_datetimefield_validate_not_required(self):
        datetimefield = DateTimeFieldFactory.create(**{'required': False})
        try:
            datetimefield.validate_input(None)
        except InputError:
            self.fail('datetimefield.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_datetimefield_validate_required_none_type(self):
        datetimefield = DateTimeFieldFactory.create(**{'required': True})
        datetimefield.validate_input(None)

    def test_datetimefield_validate_input(self):
        date_time_field = DateTimeFieldFactory()
        try:
            date_time_field.validate_input('2014-12-01')
        except InputError:
            self.fail('DateTimeField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_datetimefield_validate_false_input(self):
        date_time_field = DateTimeFieldFactory()
        date_time_field.validate_input('2014-15-01')

    def test_get_filter(self):
        date_time_field = DateTimeFieldFactory(**{'key': 'key'})
        self.assertEqual(
            date_time_field.get_filter(
                {'minval': '2014-10-31 13:00', 'maxval': '2015-02-23 12:00'}
            ),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD HH24:MI\') >= "
            "to_date(\'2014-10-31 13:00\', \'YYYY-MM-DD HH24:MI\')) AND "
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD HH24:MI\') <= "
            "to_date(\'2015-02-23 12:00\', \'YYYY-MM-DD HH24:MI\'))"
        )
        self.assertEqual(
            date_time_field.get_filter({'minval': '2014-10-31 13:00'}),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD HH24:MI\') >= "
            "to_date(\'2014-10-31 13:00\', \'YYYY-MM-DD HH24:MI\'))"
        )
        self.assertEqual(
            date_time_field.get_filter({'maxval': '2015-02-23 12:00'}),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD HH24:MI\') <= "
            "to_date(\'2015-02-23 12:00\', \'YYYY-MM-DD HH24:MI\'))"
        )


class TimeFieldTest(TestCase):
    def test_create_datefield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'TimeField'
        )
        self.assertEqual(field.__class__.__name__, 'TimeField')

    def test_get_name(self):
        field = TimeFieldFactory()
        self.assertEqual(field.type_name, 'Time')
        self.assertEqual(field.fieldtype, 'TimeField')

    def test_timefield_validate_required(self):
        timefield = TimeFieldFactory.create(**{'required': True})
        try:
            timefield.validate_input('12:45')
        except InputError:
            self.fail('timefield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_timefield_validate_inactive_required_empty_string(self):
        timefield = TimeFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            timefield.validate_input(None)
        except InputError:
            self.fail('DateField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_timefield_validate_not_required(self):
        timefield = TimeFieldFactory.create(**{'required': False})
        try:
            timefield.validate_input(None)
        except InputError:
            self.fail('timefield.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_timefield_validate_required_none_type(self):
        timefield = TimeFieldFactory.create(**{'required': True})
        timefield.validate_input(None)

    def test_timefield_validate_input(self):
        time_field = TimeFieldFactory()
        try:
            time_field.validate_input('12:45')
        except InputError:
            self.fail('DateTimeField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_timefield_validate_false_input(self):
        time_field = TimeFieldFactory()
        time_field.validate_input('25:54')

    def test_get_filter(self):
        time_field = TimeFieldFactory(**{'key': 'key'})
        self.assertEqual(
            time_field.get_filter({'minval': '8:00', 'maxval': '10:00'}),
            '((properties ->> \'key\')::time >= \'8:00\'::time) AND '
            '((properties ->> \'key\')::time <= \'10:00\'::time)'
        )
        self.assertEqual(
            time_field.get_filter({'minval': '21:00', 'maxval': '3:00'}),
            '((properties ->> \'key\')::time >= \'21:00\'::time) OR '
            '((properties ->> \'key\')::time <= \'3:00\'::time)'
        )
        self.assertEqual(
            time_field.get_filter({'minval': '21:00'}),
            '((properties ->> \'key\')::time >= \'21:00\'::time)'
        )
        self.assertEqual(
            time_field.get_filter({'maxval': '21:00'}),
            '((properties ->> \'key\')::time <= \'21:00\'::time)'
        )


class DateFieldTest(TestCase):
    def test_create_datefield(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'DateField'
        )
        self.assertEqual(field.__class__.__name__, 'DateField')

    def test_get_name(self):
        field = DateFieldFactory()
        self.assertEqual(field.type_name, 'Date')
        self.assertEqual(field.fieldtype, 'DateField')

    def test_datefield_validate_required(self):
        datefield = DateFieldFactory.create(**{'required': True})
        try:
            datefield.validate_input('2014-01-01')
        except InputError:
            self.fail('datefield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_datefield_validate_inactive_required_empty_string(self):
        datefield = DateFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            datefield.validate_input(None)
        except InputError:
            self.fail('DateField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_datefield_validate_not_required(self):
        datefield = DateFieldFactory.create(**{'required': False})
        try:
            datefield.validate_input(None)
        except InputError:
            self.fail('datefield.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_datefield_validate_required_none_type(self):
        datetimefield = DateFieldFactory.create(**{'required': True})
        datetimefield.validate_input(None)

    def test_datefield_validate_input(self):
        date_time_field = DateFieldFactory()
        try:
            date_time_field.validate_input('2014-12-01')
        except InputError:
            self.fail('DateTimeField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_datefield_validate_false_input(self):
        date_time_field = DateFieldFactory()
        date_time_field.validate_input('2014-15-01')

    def test_get_filter(self):
        date_field = DateFieldFactory(**{'key': 'key'})
        self.assertEqual(
            date_field.get_filter(
                {'minval': '2014-10-31', 'maxval': '2015-02-23'}
            ),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD\') >= "
            "to_date(\'2014-10-31\', \'YYYY-MM-DD\')) AND "
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD\') <= "
            "to_date(\'2015-02-23\', \'YYYY-MM-DD\'))"
        )
        self.assertEqual(
            date_field.get_filter({'minval': '2014-10-31'}),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD\') >= "
            "to_date(\'2014-10-31\', \'YYYY-MM-DD\'))"
        )
        self.assertEqual(
            date_field.get_filter({'maxval': '2015-02-23'}),
            "(to_date(properties ->> \'key\', \'YYYY-MM-DD\') <= "
            "to_date(\'2015-02-23\', \'YYYY-MM-DD\'))"
        )


class MultipleLookupTest(TestCase):
    def test_create(self):
        category = CategoryFactory()
        field = Field.create(
            'name', 'key', 'description', False, category,
            'MultipleLookupField'
        )
        self.assertEqual(field.__class__.__name__, 'MultipleLookupField')

    def test_get_name(self):
        field = MultipleLookupFieldFactory.create()
        self.assertEqual(field.type_name, 'Multiple select')
        self.assertEqual(field.fieldtype, 'MultipleLookupField')

    def test_convert_from_string(self):
        field = MultipleLookupFieldFactory.create()

        self.assertEqual(None, field.convert_from_string(''))
        self.assertEqual([1, 2, 3], field.convert_from_string('[1, 2, 3]'))

    def test_validate_required(self):
        field = MultipleLookupFieldFactory.create(**{'required': True})
        lookup_value_1 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        lookup_value_2 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        try:
            field.validate_input(
                json.dumps([lookup_value_1.id, lookup_value_2.id])
            )
        except InputError:
            self.fail('multiplelookupfield.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_validate_required_none_type(self):
        field = MultipleLookupFieldFactory.create(**{'required': True})
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        field.validate_input(None)

    def test_lookupfield_validate_not_required_none_type(self):
        field = MultipleLookupFieldFactory.create(**{'required': False})
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        try:
            field.validate_input(None)
        except InputError:
            self.fail('multiplelookupfield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_lookupfield_validate_required_inactive(self):
        field = MultipleLookupFieldFactory.create(
            **{'required': True, 'status': 'inactive'})
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        try:
            field.validate_input(None)
        except InputError:
            self.fail('multiplelookupfield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_validate_string_input(self):
        field = MultipleLookupFieldFactory.create(
            **{'required': True, 'status': 'inactive'})
        lookup_value_1 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        lookup_value_2 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        try:
            field.validate_input(
                json.dumps([lookup_value_1.id, lookup_value_2.id])
            )
            field.validate_input(json.dumps([lookup_value_1.id]))
        except InputError:
            self.fail('multiplelookupfield.validate_input() raised InputError '
                      'unexpectedly!')

    def test_validate_input(self):
        field = MultipleLookupFieldFactory.create(
            **{'required': True, 'status': 'inactive'})
        lookup_value_1 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        lookup_value_2 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        try:
            field.validate_input([lookup_value_1.id, lookup_value_2.id])
            field.validate_input([lookup_value_1.id])
        except InputError:
            self.fail('multiplelookupfield.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_validate_wrong_input(self):
        field = MultipleLookupFieldFactory.create(
            **{'required': True, 'status': 'inactive'})
        lookup_value_1 = MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        MultipleLookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': field
        })
        field.validate_input(json.dumps([lookup_value_1.id, 8986552121]))

    def test_get_filter(self):
        lookup_field = MultipleLookupFieldFactory(**{'key': 'key'})
        self.assertEqual(
            lookup_field.get_filter([1, 2, 3]),
            '(regexp_split_to_array(btrim(properties ->> \'key\', \'[]\'), '
            '\',\')::int[] && ARRAY[1, 2, 3])'
        )
