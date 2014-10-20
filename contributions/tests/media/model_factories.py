import factory
from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile

from users.tests.model_factories import UserF
from contributions.tests.model_factories import ObservationFactory
from contributions.models import ImageFile, VideoFile


def get_image():
    image_file = StringIO()
    image = Image.new('RGBA', size=(50, 50), color=(256, 0, 0))
    image.save(image_file, 'png')
    image_file.seek(0)

    return ContentFile(image_file.read(), 'test.png')


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
    youtube_link = 'http://example.com/98aishfijh'
    swf_link = 'http://example.com/98aishfijh'
