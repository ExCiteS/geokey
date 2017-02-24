"""Tests for models of logger."""

from django.test import TestCase

from geokey.users.tests.model_factories import UserFactory, UserGroupFactory
from geokey.projects.tests.model_factories import ProjectFactory
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.contributions.tests.model_factories import (
    LocationFactory,
    ObservationFactory,
    CommentFactory,
)
from geokey.subsets.tests.model_factories import SubsetFactory

from ..models import LoggerHistory


class LoggerHistoryTest(TestCase):

    # TESTING USERS
    def test_log_create_user(self):
        log_count_init = LoggerHistory.objects.count()
        user = UserFactory.create()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_user(self):
        user = UserFactory.create()
        log_count_init = LoggerHistory.objects.count()
        user.display_name = 'New name'
        user.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_deleted_user(self):
        user = UserFactory.create()
        user_id = user.id
        log_count_init = LoggerHistory.objects.count()
        user.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user_id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING PROJECTS
    def test_log_create_project(self):
        user = UserFactory.create()
        log_count_init = LoggerHistory.objects.count()
        project = ProjectFactory.create(**{'creator': user})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_deleted_project(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        project.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_name(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        project.name = 'New Name'
        project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Project renamed')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_project_permissions(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        project.everyone_contributes = 'auth'
        project.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Project permissions changed')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING USERGROUPS
    def test_log_create_usergroup(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        usergroup = UserGroupFactory.create(**{'project': project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.usergroup_id), usergroup.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_usergroup(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        usergroup = UserGroupFactory.create(**{'project': project})
        log_count_init = LoggerHistory.objects.count()
        usergroup.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.usergroup_id), usergroup.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_usergroup_name(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        usergroup = UserGroupFactory.create(**{'project': project})
        log_count_init = LoggerHistory.objects.count()
        usergroup.name = 'New Name'
        usergroup.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.usergroup_id), usergroup.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'User group renamed')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING CATEGORIES
    def test_log_create_category(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_deleted_category(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        log_count_init = LoggerHistory.objects.count()
        category.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_category_name(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        log_count_init = LoggerHistory.objects.count()
        category.name = 'New Name'
        category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Category renamed')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_category_status(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        log_count_init = LoggerHistory.objects.count()
        category.status = 'inactive'
        category.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Category is inactive')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING SUBSETS
    def test_log_create_subset(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        subset = SubsetFactory.create(**{
            'creator': user,
            'project': project})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.subset_id), subset.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_subset(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        subset = SubsetFactory.create(**{
            'creator': user,
            'project': project})
        log_count_init = LoggerHistory.objects.count()
        subset.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.subset_id), subset.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_subset_name(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        subset = SubsetFactory.create(**{
            'creator': user,
            'project': project})
        log_count_init = LoggerHistory.objects.count()
        subset.name = 'New Name'
        subset.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.subset_id), subset.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Subset renamed')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING OBSERVATIONS
    def test_log_create_observation(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        location = LocationFactory.create(**{'creator': user})
        log_count_init = LoggerHistory.objects.count()
        observation = ObservationFactory.create(**{
            'creator': user,
            'project': project,
            'category': category,
            'location': location})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(int(log.location_id), location.id)
        self.assertEqual(int(log.observation_id), observation.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_observation(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        location = LocationFactory.create(**{'creator': user})
        observation = ObservationFactory.create(**{
            'creator': user,
            'project': project,
            'category': category,
            'location': location})
        log_count_init = LoggerHistory.objects.count()
        observation.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(int(log.location_id), location.id)
        self.assertEqual(int(log.observation_id), observation.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    # TESTING COMMENTS
    def test_log_craete_comment(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        location = LocationFactory.create(**{'creator': user})
        observation = ObservationFactory.create(**{
            'creator': user,
            'project': project,
            'category': category,
            'location': location})
        log_count_init = LoggerHistory.objects.count()
        comment = CommentFactory.create(**{
            'creator': user,
            'commentto': observation})

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(int(log.location_id), location.id)
        self.assertEqual(int(log.observation_id), observation.id)
        self.assertEqual(int(log.comment_id), comment.id)
        self.assertEqual(str(log.action_id), 'created')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_delete_comment(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        location = LocationFactory.create(**{'creator': user})
        observation = ObservationFactory.create(**{
            'creator': user,
            'project': project,
            'category': category,
            'location': location})
        comment = CommentFactory.create(**{
            'creator': user,
            'commentto': observation})
        log_count_init = LoggerHistory.objects.count()
        comment.delete()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(int(log.location_id), location.id)
        self.assertEqual(int(log.observation_id), observation.id)
        self.assertEqual(int(log.comment_id), comment.id)
        self.assertEqual(str(log.action_id), 'deleted')
        self.assertEqual(log_count, log_count_init + 1)

    def test_log_update_comment(self):
        user = UserFactory.create()
        project = ProjectFactory.create(**{'creator': user})
        category = CategoryFactory.create(**{
            'creator': user,
            'project': project})
        location = LocationFactory.create(**{'creator': user})
        observation = ObservationFactory.create(**{
            'creator': user,
            'project': project,
            'category': category,
            'location': location})
        comment = CommentFactory.create(**{
            'creator': user,
            'commentto': observation})
        log_count_init = LoggerHistory.objects.count()
        comment.review_status = 'resolved'
        comment.save()

        log = LoggerHistory.objects.last()
        log_count = LoggerHistory.objects.count()

        self.assertEqual(int(log.user_id), user.id)
        self.assertEqual(int(log.project_id), project.id)
        self.assertEqual(int(log.category_id), category.id)
        self.assertEqual(int(log.location_id), location.id)
        self.assertEqual(int(log.observation_id), observation.id)
        self.assertEqual(int(log.comment_id), comment.id)
        self.assertEqual(str(log.action_id), 'updated')
        self.assertEqual(str(log.action), 'Comment review status to resolved')
        self.assertEqual(log_count, log_count_init + 1)
