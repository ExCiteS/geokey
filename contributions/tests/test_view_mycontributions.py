import json
from contributions.tests.model_factories import ObservationFactory
from django.core.urlresolvers import reverse

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from projects.tests.model_factories import UserF, ProjectF
from dataviews.tests.model_factories import ViewFactory

from ..views import MyObservations


class MyContributionsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.contributor = UserF.create()
        self.some_dude = UserF.create()

        self.project = ProjectF.create(add_contributors=[self.contributor])

        for x in range(0, 5):
            ObservationFactory.create(**{
                'project': self.project,
                'creator': self.contributor
            })
            ObservationFactory.create(**{
                'project': self.project,
                'creator': self.some_dude
            })

    def get(self, user):
        url = reverse('api:project_my_observations', kwargs={
            'project_id': self.project.id
        })
        request = self.factory.get(url)
        force_authenticate(request, user=user)
        theview = MyObservations.as_view()
        return theview(
            request,
            project_id=self.project.id).render()

    def test_my_contributions_view(self):
        response = self.get(self.contributor)

        self.assertEqual(response.status_code, 200)
        objects = json.loads(response.content)
        self.assertEqual(len(objects.get('features')), 5)

    def test_my_contributions_with_non_member(self):
        user = UserF.create()

        response = self.get(user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            'You are not allowed to access this project.',
            json.loads(response.content).get('error')
        )

    def test_my_contributions_with_non_contributor(self):
        view_user = UserF.create()
        ViewFactory(add_viewers=[view_user], **{
            'project': self.project
        })

        response = self.get(view_user)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            'You are not eligable to contribute data to this project',
            json.loads(response.content).get('error')
        )
