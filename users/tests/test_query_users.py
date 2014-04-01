import json

from django.test import TestCase

from .model_factories import UserF


class QueryUsersTest(TestCase):
    def _get(self, query):
        # self.client.login(username=user.username, password='123456')
        return self.client.get('/ajax/users/?query=' + query)

    def setUp(self):
        UserF.create(**{
            'username': 'peter',
            'first_name': 'Peter',
            'last_name': 'Schmeichel'
        })
        UserF.create(**{
            'username': 'george',
            'first_name': 'George',
            'last_name': 'Best'
        })
        UserF.create(**{
            'username': 'luis',
            'first_name': 'Luis',
            'last_name': 'Figo'
        })
        UserF.create(**{
            'username': 'pete23',
            'first_name': 'Peter',
        })
        UserF.create(**{
            'username': 'pet48',
            'first_name': 'Frank',
            'last_name': 'Frank Lehmann'
        })
        UserF.create(**{
            'username': 'frank',
            'first_name': 'Frank',
            'last_name': 'Frank Lampard'
        })

    def test_query_pet(self):
        response = self._get('pet')

        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 3)
        self.assertContains(response, 'Schmeichel')
        self.assertContains(response, 'Lehmann')
        self.assertContains(response, 'pete23')

    def test_query_peter(self):
        response = self._get('peter')
        result_set = json.loads(response.content)
        self.assertEqual(len(result_set), 2)
        self.assertContains(response, 'Schmeichel')
        self.assertContains(response, 'pete23')
