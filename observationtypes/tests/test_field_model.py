from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF, UserGroupF
from core.exceptions import InputError

from ..models import Field

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    FieldFactory, ObservationTypeFactory
)


class FieldTest(TestCase):
    def test_access_fields_with_admin(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        self.assertEqual(
            len(Field.objects.get_list(admin, project.id, observation_type.id)), 2
        )

    def test_access_active_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    def test_access_inactive_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    def test_admin_access_active_field_with_admin(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.as_admin(
                user, project.id, observation_type.id, field.id))

    def test_access_fields_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        inactive = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        fields = Field.objects.get_list(user, project.id, observation_type.id)
        self.assertEqual(len(fields), 1)
        self.assertNotIn(inactive, fields)

    def test_access_active_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        self.assertEqual(
            field, Field.objects.get_single(
                user, project.id, observation_type.id, field.id))

    @raises(PermissionDenied)
    def test_access_inactive_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(PermissionDenied)
    def test_admin_access_active_field_with_contributor(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.as_admin(
            user, project.id, observation_type.id, field.id)

    @raises(PermissionDenied)
    def test_access_fields_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_list(user, project.id, observation_type.id)

    @raises(PermissionDenied)
    def test_access_active_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(PermissionDenied)
    def test_access_inactive_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'inactive',
            'observationtype': observation_type
        })
        Field.objects.get_single(
            user, project.id, observation_type.id, field.id)

    @raises(PermissionDenied)
    def test_admin_access_active_field_with_non_member(self):
        user = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True
        })
        observation_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        field = TextFieldFactory.create(**{
            'status': 'active',
            'observationtype': observation_type
        })
        Field.objects.as_admin(
            user, project.id, observation_type.id, field.id)

    @raises(NotImplementedError)
    def test_field_validate_input(self):
        field = FieldFactory()
        field.validate_input('Bla')

    def test_create_textfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'TextField')
        self.assertEqual(field.__class__.__name__, 'TextField')

    def test_create_numericfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'NumericField')
        self.assertEqual(field.__class__.__name__, 'NumericField')

    def test_create_truefalsefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'TrueFalseField')
        self.assertEqual(field.__class__.__name__, 'TrueFalseField')

    def test_create_datetimefield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'DateTimeField')
        self.assertEqual(field.__class__.__name__, 'DateTimeField')

    def test_create_lookupfield(self):
        observation_type = ObservationTypeFactory()
        field = Field.create(
            'name', 'key', 'description', False, observation_type, 'LookupField')
        self.assertEqual(field.__class__.__name__, 'LookupField')

    def test_get_name(self):
        field = TextFieldFactory()
        self.assertEqual(field.get_type_name(), 'Text')

    #
    # TEXT FIELD
    #
    def test_textfield_validate_input(self):
        textfield = TextFieldFactory()
        try:
            textfield.validate_input('Bla')
        except InputError:
            self.fail('TextField.validate_input() raised InputError '
                      'unexpectedly!')

    def test_textfield_convert_from_String(self):
        textfield = TextFieldFactory()
        self.assertEqual('Bla', textfield.convert_from_string('Bla'))

    #
    # NUMERIC FIELD
    #

    def test_numericfield_validate_input_number(self):
        numeric_field = NumericFieldFactory()
        try:
            numeric_field.validate_input(158)
        except InputError:
            self.fail('NumericField.validate_input() raised InputError '
                      'unexpectedly!')

    @raises(InputError)
    def test_numericfield_validate_input_string_number(self):
        numeric_field = NumericFieldFactory()
        numeric_field.validate_input('12')

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

    #
    # DATE TIME FIELD
    #
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

    #
    # TRUE FALSE FIELD
    #

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
    def test_truefalsefield_validate_input_none_type(self):
        true_false_field = TrueFalseFieldFactory()
        true_false_field.validate_input(None)

    @raises(InputError)
    def test_truefalsefield_validate_input_number(self):
        true_false_field = TrueFalseFieldFactory()
        true_false_field.validate_input(12)

    def test_truefalsefield_convert_from_string(self):
        true_false_field = TrueFalseFieldFactory()
        self.assertTrue(true_false_field.convert_from_string('True'))
        self.assertFalse(true_false_field.convert_from_string('False'))

    #
    # LOOKUP FIELD
    #

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
