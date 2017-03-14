"""Tests for logger: model Comment."""

from django.test import TestCase

from geokey.core.models import LoggerHistory
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory,
    CommentFactory,
)


class LogCommentTest(TestCase):
    """Test model Comment."""

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
        self.comment = CommentFactory.create(**{
            'creator': self.user,
            'commentto': self.observation})

    def test_log_create(self):
        """Test when comment gets created."""
        log_count_init = LoggerHistory.objects.count()
        comment = CommentFactory.create(**{
            'creator': self.user,
            'commentto': self.observation})

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
        self.assertEqual(log.comment, {
            'id': str(comment.id)})
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Comment'})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_create_response(self):
        """Test when response gets created."""
        log_count_init = LoggerHistory.objects.count()
        response = CommentFactory.create(**{
            'creator': self.user,
            'commentto': self.observation,
            'respondsto': self.comment})

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
        self.assertEqual(log.comment, {
            'id': str(response.id)})
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'created',
            'class': 'Comment',
            'subaction': 'respond',
            'comment_id': str(self.comment.id)})
        self.assertEqual(log_count, log_count_init + 1)
        self.assertEqual(log.historical, None)

    def test_log_delete(self):
        """Test when comment gets deleted."""
        log_count_init = LoggerHistory.objects.count()
        self.comment.delete()

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
        self.assertEqual(log.comment, {
            'id': str(self.comment.id)})
        self.assertEqual(log.subset, None)
        self.assertEqual(log.action, {
            'id': 'deleted',
            'class': 'Comment',
            'field': 'status',
            'value': 'deleted'})
        self.assertEqual(log_count, log_count_init + 1)
        history = self.comment.history.get(pk=log.historical.get('id'))
        self.assertEqual(history.id, self.comment.id)

    def test_log_delete_nested(self):
        """Test when comment that has responses gets deleted."""
        response = CommentFactory.create(**{
            'creator': self.user,
            'commentto': self.observation,
            'respondsto': self.comment})
        log_count_init = LoggerHistory.objects.count()
        self.comment.delete()

        log_count = LoggerHistory.objects.count()
        self.assertEqual(log_count, log_count_init + 2)

        logs = LoggerHistory.objects.all().order_by('-pk')[:2]

        # Response gets deleted
        self.assertNotEqual(logs[1].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[1].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[1].usergroup, None)
        self.assertEqual(logs[1].category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(logs[1].field, None)
        self.assertEqual(logs[1].location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(logs[1].observation, {
            'id': str(self.observation.id)})
        self.assertEqual(logs[1].comment, {
            'id': str(response.id)})
        self.assertEqual(logs[1].subset, None)
        self.assertEqual(logs[1].action, {
            'id': 'deleted',
            'class': 'Comment',
            'subaction': 'respond',
            'comment_id': str(self.comment.id)})
        self.assertEqual(logs[1].historical, None)

        # Comment gets deleted
        self.assertNotEqual(logs[0].user, {
            'id': str(self.user.id),
            'display_name': self.user.display_name})
        self.assertEqual(logs[0].project, {
            'id': str(self.project.id),
            'name': self.project.name})
        self.assertEqual(logs[0].usergroup, None)
        self.assertEqual(logs[0].category, {
            'id': str(self.category.id),
            'name': self.category.name})
        self.assertEqual(logs[0].field, None)
        self.assertEqual(logs[0].location, {
            'id': str(self.location.id),
            'name': self.location.name})
        self.assertEqual(logs[0].observation, {
            'id': str(self.observation.id)})
        self.assertEqual(logs[0].comment, {
            'id': str(self.comment.id)})
        self.assertEqual(logs[0].subset, None)
        self.assertEqual(logs[0].action, {
            'id': 'deleted',
            'class': 'Comment',
            'field': 'status',
            'value': 'deleted'})
        history = self.comment.history.get(pk=logs[0].historical.get('id'))
        self.assertEqual(history.id, self.comment.id)
