"""Tests for logger: model VideoFile."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory,
)
from geokey.contributions.tests.media.model_factories import VideoFileFactory


class LogVideoFileTest(TestCase):
    """Test model VideoFile."""

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
        self.videofile = VideoFileFactory.create(**{
            'creator': self.user,
            'contribution': self.observation})

    def test_log_create(self):
        """Test when video file is created gets created."""
        log_count_init = LoggerHistory.objects.count()
        videofile = VideoFileFactory.create(**{
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
        self.assertEqual(log.comment, None)
        self.assertEqual(log.mediafile, {
            'id': str(videofile.id),
            'name': videofile.name,
            'type': 'VideoFile'})
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'MediaFile'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when video file gets deleted."""
        mediafile_id = self.videofile.id
        mediafile_name = self.videofile.name
        log_count_init = LoggerHistory.objects.count()
        self.videofile.delete()

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
        self.assertEqual(log.comment, None)
        self.assertEqual(log.mediafile, {
            'id': str(mediafile_id),
            'name': mediafile_name,
            'type': 'VideoFile'})
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'MediaFile',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)
