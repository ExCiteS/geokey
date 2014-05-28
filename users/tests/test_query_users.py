import json

from django.test import TestCase

from .model_factories import UserF


class QueryUsersTest(TestCase):
    def _get(self, query):
        # self.client.login(username=user.username, password='123456')
        return self.client.get('/ajax/users/?query=' + query)

    def setUp(self):
        UserF.create(**{
            'display_name': 'Peter Schmeichel'
        })
        UserF.create(**{
            'display_name': 'George Best'
        })
        UserF.create(**{
            'display_name': 'Luis Figo'
        })
        UserF.create(**{
            'display_name': 'pete23'
        })
        UserF.create(**{
            'display_name': 'pet48'
        })
        UserF.create(**{
            'display_name': 'Frank Lampard'
        })

    def test_query_pet(self):
        response = self._get('pet')

        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 3)
        self.assertContains(response, 'Schmeichel')
        self.assertContains(response, 'pete23')
        self.assertContains(response, 'pet48')

    def test_query_peter(self):
        response = self._get('peter')
        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 1)
        self.assertContains(response, 'Schmeichel')
