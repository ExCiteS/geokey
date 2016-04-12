"""Model factories used for tests of projects."""

import datetime
import factory

from django.contrib.gis.geos import GEOSGeometry

from geokey.users.tests.model_factories import UserFactory, UserGroupFactory

from geokey.projects.models import Project, Admins


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    isprivate = True
    islocked = False
    everyone_contributes = 'false'
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserFactory)
    status = 'active'
    geographic_extent = GEOSGeometry(
        '{"type": "Polygon","coordinates": [[[-0.508,51.682],[-0.53,51.327],'
        '[0.225,51.323],[0.167,51.667],[-0.508,51.682]]]}'
    )

    @factory.post_generation
    def add_admins(self, create, extracted, **kwargs):
        if not create:
            return

        Admins.objects.create(project=self, user=self.creator)
        if extracted:
            for user in extracted:
                Admins.objects.create(project=self, user=user)

    @factory.post_generation
    def add_moderators(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            UserGroupFactory(add_users=extracted, **{
                'project': self,
                'can_moderate': True
            })

    @factory.post_generation
    def add_contributors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            UserGroupFactory(add_users=extracted, **{
                'project': self,
                'can_contribute': True
            })

    @factory.post_generation
    def add_viewer(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            UserGroupFactory(add_users=extracted, **{
                'project': self,
                'can_contribute': False,
                'can_moderate': False,
            })


class AdminsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Admins

    project = factory.SubFactory(ProjectFactory)
    user = factory.SubFactory(UserFactory)
