"""Test all template tags."""

from django.test import TestCase

from geokey.core.models import LoggerHistory

from geokey.core.templatetags import logger


class TemplateTagsTest(TestCase):
    """Tests for template tags."""

    def test_check_media_file_type(self):
        """Test check the field type."""
        logger_1 = LoggerHistory.objects.create(
            user={'display_name': 'User', 'id': '5'},
            project={'name': 'Porject', 'id': '5'},
            category={'name': 'Category', 'id': '5'},
            field={'name': 'Field', 'id': '5', 'type': 'TextField'},
            action={'id': 'created', 'class': 'Field'}
        )

        field_type_1 = logger.check_field_type(logger_1.field.get('type'))
        self.assertTrue(field_type_1, 'Text field')

        logger_2 = logger_1
        logger_2.field = {'name': 'Field22', 'id': '5', 'type': 'TextField'}
        logger_2.save()
        field_type_2 = logger.check_field_type(logger_2.field.get('type'))
        self.assertTrue(field_type_2, 'Numeric field')

        logger_3 = logger_1
        logger_3.field = {'name': 'Field', 'id': '5', 'type': 'DateField'}
        logger_3.save()
        field_type_3 = logger.check_field_type(logger_3.field.get('type'))
        self.assertTrue(field_type_3, 'Date field')

        logger_4 = logger_1
        logger_4.field = {'name': 'Field', 'id': '5', 'type': 'DateTimeField'}
        logger_4.save()
        field_type_4 = logger.check_field_type(logger_4.field.get('type'))
        self.assertTrue(field_type_4, 'Date & time field')

        logger_5 = logger_1
        logger_5.field = {'name': 'Field', 'id': '5', 'type': 'LookupField'}
        logger_5.save()
        field_type_5 = logger.check_field_type(logger_5.field.get('type'))
        self.assertTrue(field_type_5, 'Select box field')

        logger_6 = logger_1
        logger_6.field = {'name': 'Field', 'id': '5', 'type': 'TimeField'}
        logger_6.save()
        field_type_6 = logger.check_field_type(logger_6.field.get('type'))
        self.assertTrue(field_type_6, 'Time field')

        logger_7 = logger_1
        logger_7.field = {
            'name': 'Field',
            'id': '5',
            'type': 'MultipleLookupField'}
        logger_7.save()
        field_type_7 = logger.check_field_type(logger_7.field.get('type'))
        self.assertTrue(field_type_7, 'Multiple select field')

    def test_check_field_type(self):
        """Test check the field type."""
        logger_11 = LoggerHistory.objects.create(
            user={'display_name': 'User', 'id': '5'},
            project={'name': 'Porject', 'id': '5'},
            category={'name': 'Category', 'id': '5'},
            mediafile={'name': 'MediaFile', 'id': '43', 'type': 'AudioFile'},
            action={'id': 'created', 'class': 'MediaFile'}
        )

        file_type_11 = logger.check_media_file_type(
            logger_11.mediafile.get('type'))
        self.assertTrue(file_type_11, 'Audio file')

        logger_22 = logger_11
        logger_22.mediafile = {
            'name': 'MediaFile',
            'id': '77',
            'type': 'VideoFile'}
        logger_22.save()
        file_type_22 = logger.check_media_file_type(
            logger_22.mediafile.get('type'))
        self.assertTrue(file_type_22, 'Video file')

        logger_33 = logger_11
        logger_33.mediafile = {
            'name': 'MediaFile',
            'id': '66',
            'type': 'ImageFile'}
        logger_33.save()
        file_type_33 = logger.check_media_file_type(
            logger_33.mediafile.get('type'))
        self.assertTrue(file_type_33, 'Image file')
