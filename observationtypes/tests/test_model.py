from django.test import TestCase

from nose.tools import raises

from core.exceptions import InputError

from ..models import Field

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    FieldFactory, ObservationTypeFactory
)


class FieldTest(TestCase):
    @raises(NotImplementedError)
    def test_field_validate_input(self):
        field = FieldFactory()
        field.validate_input('Bla')

    def test_get_field_types(self):
        field_types = Field.get_field_types()
        self.assertEqual(len(field_types), 5)


class TextFieldTest(TestCase):
    def test_create_textfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type,
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


class NumericFieldTest(TestCase):
    def test_create_numericfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type,
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

    def test_numericfield_convert_from_empty_string(self):
        numeric_field = NumericFieldFactory()
        self.assertEqual(None, numeric_field.convert_from_string(''))


class TrueFalseFieldTest(TestCase):
    def test_create_truefalsefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type,
            'TrueFalseField'
        )
        self.assertEqual(field.__class__.__name__, 'TrueFalseField')

    def test_get_name(self):
        field = TrueFalseFieldFactory()
        self.assertEqual(field.type_name, 'True/False')
        self.assertEqual(field.fieldtype, 'TrueFalseField')

    def test_truefalsefield_validate_required(self):
        true_false_field = TrueFalseFieldFactory.create(**{'required': True})
        true_false_field.validate_input(True)

    @raises(InputError)
    def test_truefalsefield_validate_required_none_type(self):
        true_false_field = TrueFalseFieldFactory.create(**{'required': True})
        true_false_field.validate_input(None)

    def test_truefalsefield_validate_inactive_required_empty_string(self):
        true_false_field = TrueFalseFieldFactory.create(**{
            'required': True,
            'status': 'inactive'}
        )
        try:
            true_false_field.validate_input(None)
        except InputError:
            self.fail('TrueFalseField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_truefalsefield_validate_input(self):
        true_false_field = TrueFalseFieldFactory()
        try:
            true_false_field.validate_input(True)
            true_false_field.validate_input(False)
        except InputError:
            self.fail('TrueFalseField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_truefalsefield_validate_input_string(self):
        true_false_field = TrueFalseFieldFactory()
        true_false_field.validate_input('bla')

    @raises(InputError)
    def test_truefalsefield_validate_input_number(self):
        true_false_field = TrueFalseFieldFactory()
        true_false_field.validate_input(12)

    def test_truefalsefield_convert_from_string(self):
        true_false_field = TrueFalseFieldFactory()
        self.assertTrue(true_false_field.convert_from_string('True'))
        self.assertFalse(true_false_field.convert_from_string('False'))


class SingleLookupFieldTest(TestCase):
    def test_create_lookupfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type,
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


class DateTimeFieldTest(TestCase):
    def test_create_datetimefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type,
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
