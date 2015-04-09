import datetime
from django.test import TestCase

from geokey.categories.tests.model_factories import (
    TextFieldFactory, NumericFieldFactory, DateFieldFactory,
    LookupFieldFactory, LookupValueFactory, MultipleLookupValueFactory,
    MultipleLookupFieldFactory, CategoryFactory, DateTimeFieldFactory,
    TimeFieldFactory
)
from geokey.projects.tests.model_factories import ProjectF
from geokey.datagroupings.tests.model_factories import GroupingFactory
from geokey.users.tests.model_factories import (
    UserGroupF, GroupingUserGroupFactory
)

from geokey.datagroupings.tests.model_factories import RuleFactory

from ..templatetags.is_in import is_in
from ..templatetags.key import key, value, minval, maxval
from ..templatetags.filters import (
    get_textfield_filter, get_numericfield_filter, get_datefield_filter,
    get_singlelookup_filter, get_multiplelookup_filter, get_createdate_filter,
    filters
)
from ..templatetags.usergroups import get_user_group, usergroups


class TemplateTagsTest(TestCase):
    def test_is_in(self):
        dict = {
            'name': ["1", "2", "3"]
        }
        self.assertEqual(is_in(1, 'name', dict), 'selected')
        self.assertEqual(is_in(4, 'name', dict), '')

    def test_key(self):
        dict = {
            'name': 'Oliver'
        }
        self.assertEqual(key(dict, 'name'), 'Oliver')
        self.assertEqual(key(dict, 'blah'), '')

    def test_value(self):
        dict = {
            'name': 'Oliver'
        }
        self.assertEqual(value(dict, 'name'), 'Oliver')
        self.assertEqual(value(dict, 'blah'), '')

    def test_minval(self):
        dict = {
            'field': {"minval": 5}
        }
        self.assertEqual(minval(dict, 'field'), 5)
        self.assertEqual(minval(dict, 'blah'), '')

    def test_maxval(self):
        dict = {
            'field': {"maxval": 5}
        }
        self.assertEqual(maxval(dict, 'field'), 5)
        self.assertEqual(maxval(dict, 'blah'), '')


class FilterTest(TestCase):
    def test_get_textfield_filter(self):
        field = TextFieldFactory.create(**{'name': 'Field'})
        self.assertEqual(
            get_textfield_filter(field, 'blah'),
            '<li>Field contains blah</li>'
        )

    def test_get_numericfield_filter(self):
        field = NumericFieldFactory.create(**{'name': 'Field'})
        self.assertEqual(
            get_numericfield_filter(field, {"minval": 5}),
            '<li>Field is greater than 5</li>'
        )
        self.assertEqual(
            get_numericfield_filter(field, {"maxval": 5}),
            '<li>Field is lower than 5</li>'
        )
        self.assertEqual(
            get_numericfield_filter(field, {"minval": 1, "maxval": 5}),
            '<li>Field is greater than 1 and lower than 5</li>'
        )

    def test_get_datefield_filter(self):
        field = DateFieldFactory.create(**{'name': 'Field'})
        self.assertEqual(
            get_datefield_filter(field, {"minval": "2015-03-15"}),
            '<li>Field is after 2015-03-15</li>'
        )
        self.assertEqual(
            get_datefield_filter(field, {"maxval": "2015-03-31"}),
            '<li>Field is before 2015-03-31</li>'
        )
        self.assertEqual(
            get_datefield_filter(
                field, {"minval": "2015-03-15", "maxval": "2015-03-31"}),
            '<li>Field is after 2015-03-15 and before 2015-03-31</li>'
        )

    def test_get_singlelookup_filter(self):
        field = LookupFieldFactory.create(**{'name': 'Field'})
        val_1 = LookupValueFactory.create(**{'field': field})
        val_2 = LookupValueFactory.create(**{'field': field})
        LookupValueFactory.create(**{'field': field})

        self.assertEqual(
            get_singlelookup_filter(field, [val_1.id, val_2.id]),
            '<li>Field is one of %s, %s</li>' % (val_1.name, val_2.name)
        )

    def test_get_multiplelookup_filter(self):
        field = MultipleLookupFieldFactory.create(**{'name': 'Field'})
        val_1 = MultipleLookupValueFactory.create(**{'field': field})
        val_2 = MultipleLookupValueFactory.create(**{'field': field})
        MultipleLookupValueFactory.create(**{'field': field})

        self.assertEqual(
            get_multiplelookup_filter(field, [val_1.id, val_2.id]),
            '<li>Field matches at least one of %s, %s</li>' % (
                val_1.name, val_2.name)
        )

    def test_get_createdate_filter(self):
        rule = RuleFactory.create(
            **{'min_date': datetime.datetime(2007, 12, 5, 12, 00)}
        )
        self.assertEqual(
            '<li>the contribution has been created after '
            'Dec 05 2007 12:00</li>',
            get_createdate_filter(rule)
        )

        rule = RuleFactory.create(
            **{'max_date': datetime.datetime(2012, 12, 5, 15, 00)}
        )
        self.assertEqual(
            '<li>the contribution has been created before '
            'Dec 05 2012 15:00</li>',
            get_createdate_filter(rule)
        )

        rule = RuleFactory.create(**{
            'min_date': datetime.datetime(2007, 12, 5, 12, 00),
            'max_date': datetime.datetime(2012, 12, 5, 15, 00)
        })
        self.assertEqual(
            '<li>the contribution has been created after '
            'Dec 05 2007 12:00 and before Dec 05 2012 15:00</li>',
            get_createdate_filter(rule)
        )

    def test_filters(self):
        category = CategoryFactory.create()
        TextFieldFactory.create(**{'category': category, 'key': 'text'})
        NumericFieldFactory.create(**{'category': category, 'key': 'number'})
        DateFieldFactory.create(**{'category': category, 'key': 'date'})
        DateTimeFieldFactory.create(
            **{'category': category, 'key': 'datetime'})
        TimeFieldFactory.create(**{'category': category, 'key': 'time'})
        lookup = LookupFieldFactory.create(
            **{'category': category, 'key': 'lookup'})
        val_1 = LookupValueFactory.create(**{'field': lookup})
        multiple = MultipleLookupFieldFactory.create(
            **{'category': category, 'key': 'multiple'})
        mul_1 = MultipleLookupValueFactory.create(**{'field': multiple})

        rule = RuleFactory.create(**{
            'category': category,
            'min_date': datetime.datetime(2007, 12, 5, 12, 00),
            'max_date': datetime.datetime(2012, 12, 5, 15, 00),
            'constraints': {
                'text': 'blah',
                'number': {'minval': 0, 'maxval': 10},
                'date': {'minval': 0, 'maxval': 10},
                'datetime': {'minval': 0, 'maxval': 10},
                'time': {'minval': 0, 'maxval': 10},
                'lookup': [val_1.id],
                'multiple': [mul_1.id]
            }
        })

        result = filters(rule)
        self.assertEqual(result.count('<li>'), 8)


class UserGroupsTest(TestCase):
    def test_get_user_group(self):
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        group = UserGroupF(**{'project': project})

        html = get_user_group(group, grouping)
        self.assertEqual(
            html,
            '<li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right grant-single" data-toggle="button" ><span '
            'class="text-success">Grant access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li>' % (group.id, group.name, group.description)
        )

        GroupingUserGroupFactory.create(**{
            'usergroup': group,
            'grouping': grouping
        })

        html = get_user_group(group, grouping)
        self.assertEqual(
            html,
            '<li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right active grant-single" data-toggle="button" >'
            '<span class="text-danger">Revoke access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li>' % (group.id, group.name, group.description)
        )

        project.isprivate = False
        project.save()
        grouping.isprivate = False
        grouping.save()

        html = get_user_group(group, grouping)
        self.assertEqual(
            html,
            '<li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right active grant-single" data-toggle="button" '
            'disabled="disabled">'
            '<span class="text-danger">Revoke access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li>' % (group.id, group.name, group.description)
        )

    def test_usergroups(self):
        project = ProjectF.create()
        grouping = GroupingFactory.create(**{'project': project})
        group = UserGroupF(**{'project': project})

        html = usergroups(grouping)
        self.assertEqual(
            html,
            '<ul class="list-unstyled overview-list"><li>'
            '<button type="button" name="%s" class="btn btn-default '
            'pull-right grant-single" data-toggle="button" ><span '
            'class="text-success">Grant access</span></button>'
            '<strong>%s</strong><p>%s</p>'
            '</li></ul>' % (group.id, group.name, group.description)
        )
