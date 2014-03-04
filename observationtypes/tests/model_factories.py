import factory

from projects.tests.model_factories import ProjectF

from ..models import (
    ObservationType, TextField, NumericField, TrueFalseField, DateTimeField,
    LookupField, LookupValue, Field
)


class ObservationTypeFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = ObservationType

    name = factory.Sequence(lambda n: "observationtype %s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    project = factory.SubFactory(ProjectF)
    status = 'active'


class FieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Field

    name = factory.Sequence(lambda n: "field %s" % n)
    key = factory.Sequence(lambda n: "field_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class TextFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = TextField

    name = factory.Sequence(lambda n: "textfield %s" % n)
    key = factory.Sequence(lambda n: "textfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class NumericFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = NumericField

    name = factory.Sequence(lambda n: "numericfield %s" % n)
    key = factory.Sequence(lambda n: "numericfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class TrueFalseFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = TrueFalseField

    name = factory.Sequence(lambda n: "truefalsefield %s" % n)
    key = factory.Sequence(lambda n: "truefalsefield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class DateTimeFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = DateTimeField

    name = factory.Sequence(lambda n: "datetimefield %s" % n)
    key = factory.Sequence(lambda n: "datetimefield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class LookupFieldFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = LookupField

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    key = factory.Sequence(lambda n: "lookupfield_%s" % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    observationtype = factory.SubFactory(ObservationTypeFactory)
    status = 'active'


class LookupValueFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = LookupValue

    name = factory.Sequence(lambda n: "lookupfield %s" % n)
    field = factory.SubFactory(LookupFieldFactory)
    status = 'active'
