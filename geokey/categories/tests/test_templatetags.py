"""Tests for template tags of categories."""

from django.test import TestCase

from geokey.categories.templatetags import filter_fields
from geokey.categories.tests.model_factories import (
    CategoryFactory,
    TextFieldFactory,
    NumericFieldFactory,
    DateTimeFieldFactory,
    DateFieldFactory,
    TimeFieldFactory,
    LookupFieldFactory,
    MultipleLookupFieldFactory
)


class OnlyFieldsTest(TestCase):

    def test_only_fields(self):
        category = CategoryFactory()
        TextFieldFactory(category=category)
        NumericFieldFactory(category=category)
        DateTimeFieldFactory(category=category)
        DateFieldFactory(category=category)
        TimeFieldFactory(category=category)
        LookupFieldFactory(category=category)
        MultipleLookupFieldFactory(category=category)

        all_fields = category.fields.all()

        type_names = [
            'Text',
            'Numeric',
            'Date and Time',
            'Date',
            'Time',
            'Select box',
            'Multiple select'
        ]

        for type_name in type_names:
            date_fields = filter_fields.only_fields(all_fields, type_name)
            self.assertEqual(len(date_fields), 1)
            for field in date_fields:
                self.assertEqual(field.type_name, type_name)

        date_fields = filter_fields.only_fields(
            all_fields,
            (', ').join(type_names)
        )
        self.assertEqual(len(date_fields), len(type_names))
        for field in date_fields:
                self.assertTrue(field.type_name in type_names)


class ExceptFieldsTest(TestCase):

    def test_except_fields(self):
        category = CategoryFactory()
        TextFieldFactory(category=category)
        NumericFieldFactory(category=category)
        DateTimeFieldFactory(category=category)
        DateFieldFactory(category=category)
        TimeFieldFactory(category=category)
        LookupFieldFactory(category=category)
        MultipleLookupFieldFactory(category=category)

        all_fields = category.fields.all()

        type_names = [
            'Text',
            'Numeric',
            'Date and Time',
            'Date',
            'Time',
            'Select box',
            'Multiple select'
        ]

        for type_name in type_names:
            date_fields = filter_fields.except_fields(all_fields, type_name)
            self.assertEqual(len(date_fields), len(type_names) - 1)
            for field in date_fields:
                self.assertNotEqual(field.type_name, type_name)

        date_fields = filter_fields.except_fields(
            all_fields,
            (', ').join(type_names)
        )
        self.assertEqual(len(date_fields), 0)
