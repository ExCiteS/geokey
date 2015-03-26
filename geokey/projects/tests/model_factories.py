import datetime
import factory

from django.contrib.gis.geos import GEOSGeometry

from geokey.users.tests.model_factories import UserF

from geokey.projects.models import Project, Admins


class ProjectF(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: 'project %d' % n)
    description = factory.LazyAttribute(lambda o: '%s description' % o.name)
    isprivate = True
    everyone_contributes = 'false'
    created_at = datetime.date(2014, 11, 11)
    creator = factory.SubFactory(UserF)
    status = 'active'
    geographic_extend = GEOSGeometry(
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
        from geokey.users.tests.model_factories import UserGroupF
        if not create:
            return

        if extracted:
            UserGroupF(add_users=extracted, **{
                'project': self,
                'can_moderate': True
            })

    @factory.post_generation
    def add_contributors(self, create, extracted, **kwargs):
        from geokey.users.tests.model_factories import UserGroupF
        if not create:
            return

        if extracted:
            UserGroupF(add_users=extracted, **{
                'project': self,
                'can_contribute': True
            })

    @factory.post_generation
    def add_viewers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            from geokey.datagroupings.tests.model_factories import GroupingFactory

            GroupingFactory(add_viewers=extracted, **{
                'project': self
            })


class AdminsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Admins

    project = factory.SubFactory(ProjectF)
    user = factory.SubFactory(UserF)
    contact = True
