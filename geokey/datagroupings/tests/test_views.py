import json
from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from geokey.projects.tests.model_factories import ProjectF, UserF
from geokey.categories.tests.model_factories import CategoryFactory

from ..models import Grouping, Rule
from ..views import (
    GroupingList, GroupingCreate, GroupingOverview, GroupingSettings,
    GroupingDelete, RuleCreate, RuleSettings, RuleDelete, GroupingPermissions
)

from .model_factories import GroupingFactory, RuleFactory


class GroupingListTest(TestCase):
    def test_get_context_data(self):
        view = GroupingList()
        project = ProjectF.create()

        url = reverse('admin:grouping_list', kwargs={'project_id': project.id})
        request = APIRequestFactory().get(url)
        request.user = project.creator
        view.request = request

        context = view.get_context_data(project.id)
        self.assertEqual(context.get('project'), project)


class GroupingCreateTest(TestCase):
    def test_get_with_admin(self):
        project = ProjectF.create()
        view = GroupingCreate.as_view()
        url = reverse(
            'admin:grouping_create',
            kwargs={'project_id': project.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator
        response = view(request, project_id=project.id).render()
        self.assertEqual(response.status_code, 200)

    def test_post_with_admin(self):
        data = {
            'name': 'Grouping',
            'description': ''
        }
        project = ProjectF.create()
        view = GroupingCreate.as_view()
        url = reverse(
            'admin:grouping_create',
            kwargs={'project_id': project.id}
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(request, project_id=project.id)
        self.assertEqual(response.status_code, 302)


class GroupingOverviewTest(TestCase):
    def test_get_context_data(self):
        view = GroupingOverview()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_overview',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator
        view.request = request

        context = view.get_context_data(project.id, grouping.id)
        self.assertEqual(context.get('grouping'), grouping)


class GroupingSettingsTest(TestCase):
    def test_get_with_admin(self):
        view = GroupingSettings.as_view()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_settings',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id).render()
        self.assertEqual(response.status_code, 200)

    def test_post_with_admin(self):
        data = {
            'name': 'Grouping',
            'description': ''
        }

        view = GroupingSettings.as_view()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_settings',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id)
        self.assertEqual(response.status_code, 200)


class GroupingPermissionsTest(TestCase):
    def test_get_context_data(self):
        view = GroupingPermissions()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_permissions',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator
        view.request = request

        context = view.get_context_data(project.id, grouping.id)
        self.assertEqual(context.get('grouping'), grouping)


class GroupingDeleteTest(TestCase):
    def test_get_with_admin(self):
        view = GroupingDelete.as_view()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_delete',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Grouping.objects.count(), 0)

    def test_get_with_user(self):
        user = UserF.create()
        view = GroupingDelete.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:grouping_delete',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = user

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Grouping.objects.count(), 1)


class RuleCreateTest(TestCase):
    def test_get_with_admin(self):
        user = UserF.create()
        view = RuleCreate.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:rule_create',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_user(self):
        user = UserF.create()
        view = RuleCreate.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})

        url = reverse(
            'admin:rule_create',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().get(url)
        request.user = user

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_post_with_admin(self):
        view = RuleCreate.as_view()
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        grouping = GroupingFactory.create(**{'project': project})

        data = {
            'category': category.id,
            'rules': json.dumps({
                'text': 'blah',
                'min_date': '2015-01-01',
                'max_date': '2015-10-01'
            })
        }

        url = reverse(
            'admin:rule_create',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rule.objects.count(), 1)

    def test_post_with_admin_no_rules(self):
        view = RuleCreate.as_view()
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        grouping = GroupingFactory.create(**{'project': project})

        data = {
            'category': category.id,
        }

        url = reverse(
            'admin:rule_create',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rule.objects.count(), 1)

    def test_post_with_user(self):
        user = UserF.create()
        view = RuleCreate.as_view()
        project = ProjectF.create(add_contributors=[user])
        category = CategoryFactory.create(**{'project': project})
        grouping = GroupingFactory.create(**{'project': project})

        data = {
            'category': category.id,
            'rules': json.dumps({
                'text': 'blah',
                'min_date': '2015-01-01',
                'max_date': '2015-10-01'
            })
        }

        url = reverse(
            'admin:rule_create',
            kwargs={'project_id': project.id, 'grouping_id': grouping.id}
        )
        request = APIRequestFactory().post(url, data)
        request.user = user

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )
        self.assertEqual(Rule.objects.count(), 0)


class RuleSettingsTest(TestCase):
    def test_get_with_admin(self):
        view = RuleSettings.as_view()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        url = reverse(
            'admin:rule_settings',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )
        request = APIRequestFactory().get(url)
        request.user = project.creator

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_get_with_user(self):
        user = UserF.create()
        view = RuleSettings.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        url = reverse(
            'admin:rule_settings',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )
        request = APIRequestFactory().get(url)
        request.user = user

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )

    def test_post_with_admin(self):
        view = RuleSettings.as_view()
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        data = {
            'category': category.id,
            'rules': json.dumps({
                'text': 'blah',
                'min_date': '2015-01-01',
                'max_date': '2015-10-01'
            })
        }

        url = reverse(
            'admin:rule_settings',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id)

        self.assertEqual(response.status_code, 302)

    def test_post_with_admin_no_rules(self):
        view = RuleSettings.as_view()
        project = ProjectF.create()
        category = CategoryFactory.create(**{'project': project})
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        data = {
            'category': category.id
        }

        url = reverse(
            'admin:rule_settings',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )
        request = APIRequestFactory().post(url, data)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id)

        self.assertEqual(response.status_code, 302)

    def test_post_with_user(self):
        user = UserF.create()
        view = RuleSettings.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})
        category = CategoryFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        url = reverse(
            'admin:rule_settings',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )

        data = {
            'category': category.id,
            'rules': json.dumps({
                'text': 'blah',
                'min_date': '2015-01-01',
                'max_date': '2015-10-01'
            })
        }

        request = APIRequestFactory().post(url, data)
        request.user = user

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )


class RuleDeleteTest(TestCase):
    def test_delete_with_admin(self):
        view = RuleDelete.as_view()
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        url = reverse(
            'admin:rule_delete',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )

        request = APIRequestFactory().get(url)
        request.user = project.creator

        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Rule.objects.count(), 0)

    def test_delete_with_user(self):
        user = UserF.create()
        view = RuleDelete.as_view()
        project = ProjectF.create(add_contributors=[user])
        grouping = GroupingFactory.create(**{'project': project})
        rule = RuleFactory.create(**{'grouping': grouping})

        url = reverse(
            'admin:rule_delete',
            kwargs={
                'project_id': project.id,
                'grouping_id': grouping.id,
                'rule_id': rule.id
            }
        )

        request = APIRequestFactory().get(url)
        request.user = user

        response = view(
            request,
            project_id=project.id,
            grouping_id=grouping.id,
            rule_id=rule.id).render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Rule.objects.count(), 1)
        self.assertContains(
            response,
            'You are not member of the administrators group of this project '
            'and therefore not allowed to alter the settings of the project'
        )
