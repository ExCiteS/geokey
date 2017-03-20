"""Custom GeoKey template tags."""

from django import template

register = template.Library()


@register.filter()
def check_media_file_type(media_file_class):
    """Check media file type and returns in a human-readble format."""
    if media_file_class == 'AudioFile':
        media_file_type = 'Audio file'
    elif media_file_class == 'VideoFile':
        media_file_type = 'Video file'
    elif media_file_class == 'ImageFile':
        media_file_type = 'Image file'

    return media_file_type


@register.filter()
def check_field_type(field_class):
    """Check field type and returns in a human-readble format."""
    if field_class == 'TextField':
        field_type = 'Text field'
    elif field_class == 'NumericField':
        field_type = 'Numeric field'
    elif field_class == 'DateField':
        field_type = 'Date field'
    elif field_class == 'DateTimeField':
        field_type = 'Date & time field'
    elif field_class == 'TimeField':
        field_type = 'Time field'
    elif field_class == 'LookupField':
        field_type = 'Select box field'
    elif field_class == 'MultipleLookupField':
        field_type = 'Multiple select field'

    return field_type
