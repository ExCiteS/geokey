from django.test import TestCase

from rest_framework.serializers import ValidationError

from .model_factories import UserF
from ..serializers import UserSerializer


class UserSerializerTest(TestCase):
    def test_validate_display_name(self):
        UserF.create(**{'display_name': 'name'})
        user = UserF.create()
        serializer = UserSerializer(user)

        try:
            serializer.validate_display_name('name')
        except ValidationError:
            pass
        else:
            self.fail('validate_display_name did not raise ValidationError')

    def test_validate_email(self):
        UserF.create(**{'email': 'name@example.com'})
        user = UserF.create()
        serializer = UserSerializer(user)

        try:
            serializer.validate_email('name@example.com')
        except ValidationError:
            pass
        else:
            self.fail('validate_email did not raise ValidationError')
