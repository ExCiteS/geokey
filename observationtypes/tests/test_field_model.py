from django.test import TestCase

from nose.tools import raises

from ..models import Field
from ..base import FIELD_TYPES

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    FieldFactory, ObservationTypeFactory
)


class FieldTest(TestCase):
    def test_create_textfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'TEXT')
        self.assertEqual(
            field.__class__.__name__, FIELD_TYPES.get('TEXT').get('model'))

    def test_create_numericfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'NUMBER')
        self.assertEqual(
            field.__class__.__name__, FIELD_TYPES.get('NUMBER').get('model'))

    def test_create_truefalsefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'TRUEFALSE')
        self.assertEqual(
            field.__class__.__name__, FIELD_TYPES.get('TRUEFALSE').get('model'))

    def test_create_datetimefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'DATETIME')
        self.assertEqual(
            field.__class__.__name__, FIELD_TYPES.get('DATETIME').get('model'))

    def test_create_lookupfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'LOOKUP')
        self.assertEqual(
            field.__class__.__name__, FIELD_TYPES.get('LOOKUP').get('model'))

    @raises(Field.DoesNotExist)
    def test_field_getinstance(self):
        field = FieldFactory()
        Field.objects.get(pk=field.id).get_instance()

    @raises(NotImplementedError)
    def test_field_validate_input(self):
        field = FieldFactory()
        field.validate_input('Bla')

    #
    # TEXT FIELD
    #
    def test_textfield_getinstance(self):
        textfield = TextFieldFactory()
        self.assertEqual(
            type(textfield),
            type(Field.objects.get(pk=textfield.id).get_instance())
        )
        self.assertEqual(
            textfield.name,
            Field.objects.get(pk=textfield.id).get_instance().name
        )

    def test_textfield_validate_input(self):
        textfield = TextFieldFactory()
        self.assertTrue(textfield.validate_input('Bla'))

    def test_textfield_convert_from_String(self):
        textfield = TextFieldFactory()
        self.assertEqual('Bla', textfield.convert_from_string('Bla'))

    #
    # NUMERIC FIELD
    #
    def test_numericfield_getinstance(self):
        numeric_field = NumericFieldFactory()
        self.assertEqual(
            type(numeric_field),
            type(Field.objects.get(pk=numeric_field.id).get_instance())
        )
        self.assertEqual(
            numeric_field.name,
            Field.objects.get(pk=numeric_field.id).get_instance().name
        )

    def test_numericfield_validate_input_number(self):
        numeric_field = NumericFieldFactory()
        self.assertTrue(numeric_field.validate_input(158))

    def test_numericfield_validate_input_string_number(self):
        numeric_field = NumericFieldFactory()
        self.assertTrue(numeric_field.validate_input('12'))

    def test_numericfield_validate_input_string_char(self):
        numeric_field = NumericFieldFactory()
        self.assertFalse(numeric_field.validate_input('bla'))

    def test_numericfield_validate_input_bool(self):
        numeric_field = NumericFieldFactory()
        self.assertFalse(numeric_field.validate_input(True))

    def test_numericfield_validate_input_minval(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10
        })
        self.assertFalse(numeric_field.validate_input(5))
        self.assertTrue(numeric_field.validate_input(12))

    def test_numericfield_validate_input_maxval(self):
        numeric_field = NumericFieldFactory(**{
            'maxval': 20
        })
        self.assertFalse(numeric_field.validate_input(21))
        self.assertTrue(numeric_field.validate_input(12))

    def test_numericfield_validate_input_minval_maxval(self):
        numeric_field = NumericFieldFactory(**{
            'minval': 10,
            'maxval': 20
        })
        self.assertFalse(numeric_field.validate_input(5))
        self.assertFalse(numeric_field.validate_input(21))
        self.assertTrue(numeric_field.validate_input(12))

    def test_numericfield_convert_from_string(self):
        numeric_field = NumericFieldFactory()
        self.assertEqual(100, numeric_field.convert_from_string('100'))

    #
    # DATE TIME FIELD
    #
    def test_datetimefield_getinstance(self):
        date_time_field = DateTimeFieldFactory()
        self.assertEqual(
            type(date_time_field),
            type(Field.objects.get(pk=date_time_field.id).get_instance())
        )
        self.assertEqual(
            date_time_field.name,
            Field.objects.get(pk=date_time_field.id).get_instance().name
        )

    def test_datetimefield_validate_input(self):
        date_time_field = DateTimeFieldFactory()
        self.assertTrue(date_time_field.validate_input('2014-12-01'))
        self.assertFalse(date_time_field.validate_input('2014-15-01'))

    #
    # TRUE FALSE FIELD
    #
    def test_truefalsefield_getinstance(self):
        true_false_field = TrueFalseFieldFactory()
        self.assertEqual(
            type(true_false_field),
            type(Field.objects.get(pk=true_false_field.id).get_instance())
        )
        self.assertEqual(
            true_false_field.name,
            Field.objects.get(pk=true_false_field.id).get_instance().name
        )

    def test_truefalsefield_validate_input(self):
        true_false_field = TrueFalseFieldFactory()
        self.assertTrue(true_false_field.validate_input(True))
        self.assertTrue(true_false_field.validate_input('true'))
        self.assertTrue(true_false_field.validate_input(1))
        self.assertTrue(true_false_field.validate_input(False))
        self.assertTrue(true_false_field.validate_input('false'))
        self.assertTrue(true_false_field.validate_input(0))
        self.assertFalse(true_false_field.validate_input('bla'))
        self.assertFalse(true_false_field.validate_input(None))
        self.assertFalse(true_false_field.validate_input(12))

    def test_truefalsefield_convert_from_string(self):
        true_false_field = TrueFalseFieldFactory()
        self.assertTrue(true_false_field.convert_from_string('True'))
        self.assertTrue(true_false_field.convert_from_string('1'))
        self.assertTrue(true_false_field.convert_from_string('t'))
        self.assertFalse(true_false_field.convert_from_string('False'))
        self.assertFalse(true_false_field.convert_from_string('0'))
        self.assertFalse(true_false_field.convert_from_string('f'))

    #
    # LOOKUP FIELD
    #
    def test_lookupfield_getinstance(self):
        lookup_field = LookupFieldFactory()
        self.assertEqual(
            type(lookup_field),
            type(Field.objects.get(pk=lookup_field.id).get_instance())
        )
        self.assertEqual(
            lookup_field.name,
            Field.objects.get(pk=lookup_field.id).get_instance().name
        )

    def test_lookupfield_validate_input(self):
        lookup_field = LookupFieldFactory()
        lookup_value = LookupValueFactory(**{
            'name': 'Ms. Piggy',
            'field': lookup_field
        })
        self.assertTrue(lookup_field.validate_input(lookup_value.id))
        self.assertFalse(lookup_field.validate_input(781865458))

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
