"""Tests for models of contributions (media files)."""

from django.test import TestCase

from geokey.contributions.models import (
    ImageFile, VideoFile, AudioFile,
    post_save_media_file_count_update
)
from geokey.contributions.tests.model_factories import ObservationFactory
from geokey.users.tests.model_factories import UserFactory

from .model_factories import get_image


class TestImageFilePostSave(TestCase):
    def test_post_save_image_file_count_update(self):
        observation = ObservationFactory()
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            image=get_image()
        )
        ImageFile.objects.create(
            status='deleted',
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            image=get_image()
        )

        post_save_media_file_count_update(ImageFile, instance=image_file)
        self.assertEqual(image_file.contribution.num_media, 1)
        self.assertEqual(image_file.contribution.num_comments, 0)


class ImageFileTest(TestCase):
    def test_get_type_name(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            image=get_image()
        )
        self.assertEqual(image_file.type_name, 'ImageFile')

    def test_delete_file(self):
        image_file = ImageFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            image=get_image()
        )
        image_file.delete()
        self.assertEquals(image_file.status, 'deleted')


class TestVideoFilePostSave(TestCase):
    def test_post_save_video_file_count_update(self):
        observation = ObservationFactory()
        video_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        VideoFile.objects.create(
            status='deleted',
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )

        post_save_media_file_count_update(VideoFile, instance=video_file)
        self.assertEqual(video_file.contribution.num_media, 1)
        self.assertEqual(video_file.contribution.num_comments, 0)


class VideoFileTest(TestCase):
    def test_get_type_name(self):
        video_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        self.assertEqual(video_file.type_name, 'VideoFile')

    def test_delete_file(self):
        video_file = VideoFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            video=get_image(),
            youtube_link='http://example.com/1122323',
            swf_link='http://example.com/1122323.swf'
        )
        video_file.delete()
        self.assertEquals(video_file.status, 'deleted')


class TestAudioFilePostSave(TestCase):
    def test_post_save_audio_file_count_update(self):
        observation = ObservationFactory()
        audio_file = AudioFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            audio=get_image()
        )
        AudioFile.objects.create(
            status='deleted',
            name='Test name',
            description='Test Description',
            contribution=observation,
            creator=UserFactory.create(),
            audio=get_image()
        )

        post_save_media_file_count_update(AudioFile, instance=audio_file)
        self.assertEqual(audio_file.contribution.num_media, 1)
        self.assertEqual(audio_file.contribution.num_comments, 0)


class AudioFileTest(TestCase):
    def test_get_type_name(self):
        audio_file = AudioFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            audio=get_image()
        )
        self.assertEqual(audio_file.type_name, 'AudioFile')

    def test_delete_file(self):
        audio_file = AudioFile.objects.create(
            name='Test name',
            description='Test Description',
            contribution=ObservationFactory.create(),
            creator=UserFactory.create(),
            audio=get_image()
        )
        audio_file.delete()
        self.assertEquals(audio_file.status, 'deleted')
