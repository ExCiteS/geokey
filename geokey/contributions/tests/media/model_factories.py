import factory
from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile

from geokey.users.tests.model_factories import UserF
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.contributions.models import ImageFile, VideoFile


def get_image(file_name='test.png', width=200, height=200):
    image_file = StringIO()
    image = Image.new('RGBA', size=(width, height), color=(255, 0, 255))
    image.save(image_file, 'png')
    image_file.seek(0)

    the_file = ContentFile(image_file.read(), file_name)
    the_file.content_type = 'image/png'

    return the_file


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageFile

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserF)
    contribution = factory.SubFactory(ObservationFactory)
    image = get_image()


class VideoFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VideoFile

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserF)
    contribution = factory.SubFactory(ObservationFactory)
    youtube_id = 'qb2Cd1--YvY'
    youtube_link = 'http://example.com/98aishfijh'
    swf_link = 'http://example.com/98aishfijh'
