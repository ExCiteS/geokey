from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import ProjectF, UserF
from users.tests.model_factories import GroupingUserGroupFactory, UserGroupF

from ..models import Grouping
from ..views import GroupingUpdate

from .model_factories import GroupingFactory


class ViewAjaxTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = UserF.create()
        self.contributor = UserF.create()
        self.non_member = UserF.create()

        self.project = ProjectF(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.view = GroupingFactory(**{
            'project': self.project,
            'description': 'description'
        })

    def _put(self, data, user):
        url = reverse('ajax:view', kwargs={
            'project_id': self.project.id,
            'grouping_id': self.view.id
        })
        request = self.factory.put(url, data)
        force_authenticate(request, user=user)
        theview = GroupingUpdate.as_view()
        return theview(
            request,
            project_id=self.project.id,
            grouping_id=self.view.id).render()

    def test_update_description_with_admin(self):
        response = self._put({'description': 'bockwurst'}, self.admin)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Grouping.objects.get(pk=self.view.id).description,
            'bockwurst'
        )

    def test_update_description_with_contributor(self):
        response = self._put({'description': 'bockwurst'}, self.contributor)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Grouping.objects.get(pk=self.view.id).description,
            'description'
        )

    def test_update_description_with_non_member(self):
        response = self._put({'description': 'bockwurst'}, self.non_member)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            Grouping.objects.get(pk=self.view.id).description,
            'description'
        )

    def test_update_description_with_view_member(self):
        view_member = UserF.create()
        group = UserGroupF.create(
            add_users=[view_member],
            **{'project': self.view.project}
        )
        GroupingUserGroupFactory.create(
            **{'grouping': self.view, 'usergroup': group}
        )

        response = self._put({'description': 'bockwurst'}, view_member)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Grouping.objects.get(pk=self.view.id).description,
            'description'
        )
