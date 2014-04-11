import datetime
import factory

from provider.oauth2.models import Client, AccessToken

from projects.tests.model_factories import UserF


class ClientFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Client

    user = factory.SubFactory(UserF)
    name = 'Test Client'
    url = 'http://example.com'
    redirect_uri = 'http://example.com/app'
    client_type = 1


class AccessTokenFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = AccessToken

    user = factory.SubFactory(UserF)
    token = 'aaaaasdffdsflsdkfkljdskjfkjdsfkjsdkfjklsdjfuywe8932y89y3892yr78gew7gf7wegf7yw8f9dys8998sdc78sy78cys8dyf78dsyf78ysdh7ds8fg78dsfaaaaasdffdsflsdkfkljdskjfkjdsfkjsdkfjklsdjfuywe8932y89y3892yr78gew7gf7wegf7yw8f9dys8998sdc78sy78cys8dyf78dsyf78ysdh7ds8fg78dskdsj'
    client = factory.SubFactory(ClientFactory)
    expires = datetime.date(2014, 12, 31)
    scope = 1
