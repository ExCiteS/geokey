"""Model factories used for tests of categories."""

import factory

from geokey.core.tests.helpers.image_helpers import get_image
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..models import (
    Category, TextField, NumericField, DateTimeField, DateField, TimeField,
    LookupField, LookupValue, Field, MultipleLookupField, MultipleLookupValue
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    creator = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: 'category %s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    project = factory.SubFactory(ProjectFactory)
    status = 'active'


class FieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Field

    name = factory.Sequence(lambda n: 'field %s' % n)
    key = factory.Sequence(lambda n: 'field_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False
    order = 0


class TextFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TextField

    name = factory.Sequence(lambda n: 'textfield %s' % n)
    key = factory.Sequence(lambda n: 'textfield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class NumericFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NumericField

    name = factory.Sequence(lambda n: 'numericfield %s' % n)
    key = factory.Sequence(lambda n: 'numericfield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class DateTimeFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DateTimeField

    name = factory.Sequence(lambda n: 'datetimefield %s' % n)
    key = factory.Sequence(lambda n: 'datetimefield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class DateFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DateField

    name = factory.Sequence(lambda n: 'datefield %s' % n)
    key = factory.Sequence(lambda n: 'datefield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class TimeFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TimeField

    name = factory.Sequence(lambda n: 'timefield %s' % n)
    key = factory.Sequence(lambda n: 'timefield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class LookupFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LookupField

    name = factory.Sequence(lambda n: 'lookupfield %s' % n)
    key = factory.Sequence(lambda n: 'lookupfield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class LookupValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LookupValue

    name = factory.Sequence(lambda n: 'lookupfield %s' % n)
    symbol = get_image(file_name='test_lookup_value_symbol.png')
    field = factory.SubFactory(LookupFieldFactory)
    status = 'active'


class MultipleLookupFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MultipleLookupField

    name = factory.Sequence(lambda n: 'lookupfield %s' % n)
    key = factory.Sequence(lambda n: 'lookupfield_%s' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    category = factory.SubFactory(CategoryFactory)
    status = 'active'
    required = False


class MultipleLookupValueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MultipleLookupValue

    name = factory.Sequence(lambda n: 'lookupfield %s' % n)
    symbol = get_image(file_name='test_lookup_value_symbol.png')
    field = factory.SubFactory(MultipleLookupFieldFactory)
    status = 'active'
