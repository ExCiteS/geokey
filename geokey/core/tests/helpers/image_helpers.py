"""Core image helpers."""

from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile


def get_image(file_name='test.png', width=200, height=200):
    image_file = StringIO()
    image = Image.new('RGBA', size=(width, height), color=(255, 0, 255))
    image.save(image_file, 'png')
    image_file.seek(0)

    the_file = ContentFile(image_file.read(), file_name)
    the_file.content_type = 'image/png'

    return the_file
