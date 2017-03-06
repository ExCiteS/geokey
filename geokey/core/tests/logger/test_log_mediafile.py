from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory
)
from geokey.contributions.tests.media.model_factories import (
    ImageFileFactory,
    VideoFileFactory,
    AudioFileFactory
)


class LogMediaFileTest(TestCase):
    """Test model media file."""

    def setUp(self):
        """Set up test."""
        self.user = UserFactory.create()
        self.project = ProjectFactory.create(**{
            'creator': self.user})
        self.category = CategoryFactory.create(**{
            'creator': self.user,
            'project': self.project})
        self.location = LocationFactory.create(**{
            'creator': self.user})
        self.observation = ObservationFactory.create(**{
            'creator': self.user,
            'location': self.location,
            'project': self.project,
            'category': self.category})
        # media files creation
        self.image_file = ImageFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})
        self.video_file = VideoFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})
        self.audio_file = AudioFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})

    def test_log_create_image_file(self):
        """Test when media file is created gets created."""
        log_count_init = LoggerHistory.objects.count()
        image_file = ImageFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.media_file, {
            'id': str(image_file.id),
            'name': image_file.name,
            'type': image_file.__class__.__name__})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'MediaFile'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

        video_file = VideoFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.media_file, {
            'id': str(video_file.id),
            'name': video_file.name,
            'type': video_file.__class__.__name__})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'MediaFile'})
        self.assertEqual(log_count, log_count_init + 2)
        self.assertEqual(log.historical, None)

        audio_file = AudioFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertNotEqual(log.user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(log.project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(log.usergroup, None)
        self.assertEqual(log.category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(log.field, None)
        self.assertEqual(log.location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(log.observation, {
            'id': str(self.observation.id)})
        self.assertEqual(log.media_file, {
            'id': str(audio_file.id),
            'name': audio_file.name,
            'type': audio_file.__class__.__name__})
        self.assertEqual(log.comment, None)
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'MediaFile'})
        self.assertEqual(log_count, log_count_init + 3)
        self.assertEqual(log.historical, None)
