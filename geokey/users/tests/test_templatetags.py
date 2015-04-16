from django.test import TestCase

from geokey.projects.tests.model_factories import ProjectF
from geokey.datagroupings.tests.model_factories import GroupingFactory
from .model_factories import UserGroupF, GroupingUserGroupFactory

from ..templatetags.viewgroups import get_view_group, viewgroups


class TemplateTagsTest(TestCase):
    def test_get_viewgroup(self):
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        group = UserGroupF(**{'project': project})

        html = get_view_group(grouping, group)
        self.assertEqual(
            html,
            '<li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right grant-single" data-toggle="button" >'
            '<span class="text-success">Grant access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li>' % (grouping.id, grouping.name, grouping.description)
        )

        GroupingUserGroupFactory.create(**{
            'usergroup': group,
            'grouping': grouping
        })

        html = get_view_group(grouping, group)
        self.assertEqual(
            html,
            '<li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right active grant-single" data-toggle="button" >'
            '<span class="text-danger">Revoke access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li>' % (grouping.id, grouping.name, grouping.description)
        )

        project.isprivate = False
        project.save()
        grouping.isprivate = False
        grouping.save()

        html = get_view_group(grouping, group)
        self.assertIn('This data grouping is public.', html)

    def test_viewgroups(self):
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        group = UserGroupF(**{'project': project})

        html = viewgroups(group)
        self.assertEqual(
            html,
            '<ul class="list-unstyled overview-list"><li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right grant-single" data-toggle="button" >'
            '<span class="text-success">Grant access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li></ul>' % (grouping.id, grouping.name, grouping.description)
        )
