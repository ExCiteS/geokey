from django.test import TestCase
from django.core.exceptions import PermissionDenied

from nose.tools import raises

from projects.tests.model_factories import UserF, ProjectF, UserGroupF

from .model_factories import (
    TextFieldFactory, NumericFieldFactory, DateTimeFieldFactory,
    TrueFalseFieldFactory, LookupFieldFactory, LookupValueFactory,
    FieldFactory, ObservationTypeFactory
)

from ..models import Field, ObservationType


class ObservationtypeTest(TestCase):
    #
    # ACCESS
    #
    def test_access_with_projct_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'creator': admin,
            'admins': UserGroupF(add_users=[admin]),
        })

        ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })

        self.assertEqual(
            len(ObservationType.objects.all(admin, project.id)), 2
        )

    def test_access_with_projct_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'contributors': UserGroupF(add_users=[contributor]),
        })

        active = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })

        types = ObservationType.objects.all(contributor, project.id)
        self.assertEqual(len(types), 1)
        self.assertIn(active, types)

    @raises(PermissionDenied)
    def test_access_with_projct_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create()

        ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })
        ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.all(contributor, project.id)

    def test_access_active_with_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            admin, project.id, active_type.id))

    def test_access_inactive_with_admin(self):
        admin = UserF.create()
        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        self.assertEqual(inactive_type, ObservationType.objects.get_single(
            admin, project.id, inactive_type.id))

    def test_access_active_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[contributor]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_contributor(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[contributor]),
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_single(
            contributor, project.id, inactive_type.id)

    @raises(PermissionDenied)
    def test_access_active_with_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
        })

        active_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'active'
        })

        self.assertEqual(active_type, ObservationType.objects.get_single(
            contributor, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_access_inactive_with_non_member(self):
        contributor = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
        })
        inactive_type = ObservationTypeFactory(**{
            'project': project,
            'status': 'inactive'
        })
        ObservationType.objects.get_single(
            contributor, project.id, inactive_type.id)

    def test_admin_access_with_admin(self):
        admin = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'admins': UserGroupF(add_users=[admin]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        self.assertEqual(active_type, ObservationType.objects.as_admin(
            admin, project.id, active_type.id))

    @raises(PermissionDenied)
    def test_admin_access_with_contributor(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True,
            'contributors': UserGroupF(add_users=[user]),
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)

    @raises(PermissionDenied)
    def test_admin_access_with_non_member(self):
        user = UserF.create()

        project = ProjectF.create(**{
            'isprivate': True
        })

        active_type = ObservationTypeFactory(**{
            'project': project
        })

        ObservationType.objects.as_admin(user, project.id, active_type.id)

    #
    # FIELD
    #
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
