"""Tests for template tags of projects."""

import datetime

from django.test import TestCase
from ..templatetags import count, project_attributes

from geokey.users.models import User
from geokey.projects.models import Project


class CountTest(TestCase):
    def test_more_link_text(self):
        self.assertEqual(
            count.more_link_text(6, 'category', 'categories'),
            'Show 1 more category'
        )

        self.assertEqual(
            count.more_link_text(7, 'category', 'categories'),
            'Show 2 more categories'
        )

        self.assertEqual(
            count.more_link_text(5, 'category', 'categories', 4),
            'Show 1 more category'
        )

        self.assertEqual(
            count.more_link_text(6, 'category', 'categories', 4),
            'Show 2 more categories'
        )


class ProjectAttributesTest(TestCase):
    def test_project_attributes(self):
        user = User(display_name='Test Name')
        project = Project(
            isprivate=True,
            islocked=False,
            creator=user,
            created_at=datetime.datetime.now(),
            status='active'
        )
        html = project_attributes.project_attributes(project)

        self.assertIn(
            ('Created by %s on %s') % (
                user.display_name,
                project.created_at.strftime("%d %B %Y, %H:%M")
            ),
            html
        )
        self.assertNotIn(
            'Locked',
            html)
        self.assertIn(
            '<span class="label label-primary">Private</span>',
            html)
        self.assertNotIn(
            'Archived',
            html)

        project = Project(
            isprivate=False,
            islocked=True,
            creator=user,
            created_at=datetime.datetime.now(),
            status='inactive'
        )
        html = project_attributes.project_attributes(project)

        self.assertIn(
            ('Created by %s on %s') % (
                user.display_name,
                project.created_at.strftime("%d %B %Y, %H:%M")
            ),
            html
        )
        self.assertIn(
            '<span class="label label-primary">Public</span>',
            html)
        self.assertIn(
            '<span class="label label-warning">Archived</span>',
            html)
