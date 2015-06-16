from django.test import TestCase

from geokey.projects.tests.model_factories import ProjectF
from geokey.categories.tests.model_factories import CategoryFactory
from geokey.datagroupings.tests.model_factories import GroupingFactory
from .model_factories import UserGroupF, GroupingUserGroupFactory

from ..templatetags.viewgroups import get_view_group, viewgroups
from ..templatetags import tags


class TemplateTagsTest(TestCase):
    def test_show_restrict(self):
        category = CategoryFactory.create()
        self.assertEqual(
            tags.show_restrict({str(category.id): {}}, category),
            '<a href="#" class="text-danger activate-detailed">'
            'Restrict further</a>'
        )
        self.assertEqual(
            tags.show_restrict({'2': {}}, category),
            ''
        )

    def test_is_selected(self):
        dict = ["1", "2", "3"]

        self.assertEqual(tags.is_selected(1, dict), 'selected')
        self.assertEqual(tags.is_selected(4, dict), '')

    def test_is_in(self):
        dict = {
            '1': {},
            '2': {}
        }

        self.assertTrue(tags.is_in(dict, 1))
        self.assertFalse(tags.is_in(dict, 4))

    def test_minval(self):
        self.assertEqual(tags.minval({'minval': 5}), 5)
        self.assertEqual(tags.minval({}), '')

    def test_maxval(self):
        self.assertEqual(tags.maxval({'maxval': 5}), 5)
        self.assertEqual(tags.maxval({}), '')

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
