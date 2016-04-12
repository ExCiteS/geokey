"""Model factories used for tests of contributions (media files)."""

import factory

from geokey.users.tests.model_factories import UserFactory
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.contributions.models import ImageFile, VideoFile, AudioFile
from geokey.core.tests.helpers.image_helpers import get_image


class ImageFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageFile

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    contribution = factory.SubFactory(ObservationFactory)
    image = get_image()


class VideoFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VideoFile

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    contribution = factory.SubFactory(ObservationFactory)
    youtube_id = 'qb2Cd1--YvY'
    youtube_link = 'http://example.com/98aishfijh'
    swf_link = 'http://example.com/98aishfijh'


class AudioFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AudioFile

    name = factory.Sequence(lambda n: 'name_%d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    creator = factory.SubFactory(UserFactory)
    contribution = factory.SubFactory(ObservationFactory)
    audio = get_image()
