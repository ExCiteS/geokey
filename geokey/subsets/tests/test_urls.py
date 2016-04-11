"""Tests for URLs of subsets."""

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import (
    SubsetList,
    SubsetCreate,
    SubsetSettings,
    SubsetData,
    SubsetDelete
)


class UrlsTest(TestCase):
    def test_reverse_subset_list(self):
        self.assertEqual(
            reverse('admin:subset_list', args=(3, )),
            '/admin/projects/3/subsets/'
        )

    def test_resolve_subset_list(self):
        resolved = resolve('/admin/projects/3/subsets/')
        self.assertEqual(resolved.func.__name__, SubsetList.__name__)
        self.assertEqual(resolved.kwargs['project_id'], '3')

    def test_reverse_subset_create(self):
        self.assertEqual(
            reverse('admin:subset_create', args=(3, )),
            '/admin/projects/3/subsets/new/'
        )

    def test_resolve_subset_create(self):
        resolved = resolve('/admin/projects/3/subsets/new/')
        self.assertEqual(resolved.func.__name__, SubsetCreate.__name__)
        self.assertEqual(resolved.kwargs['project_id'], '3')

    def test_reverse_subset_settings(self):
        self.assertEqual(
            reverse('admin:subset_settings', args=(3, 5, )),
            '/admin/projects/3/subsets/5/'
        )

    def test_resolve_subset_settings(self):
        resolved = resolve('/admin/projects/3/subsets/5/')
        self.assertEqual(resolved.func.__name__, SubsetSettings.__name__)
        self.assertEqual(resolved.kwargs['project_id'], '3')
        self.assertEqual(resolved.kwargs['subset_id'], '5')

    def test_reverse_subset_delete(self):
        self.assertEqual(
            reverse('admin:subset_delete', args=(3, 5, )),
            '/admin/projects/3/subsets/5/delete/'
        )

    def test_resolve_subset_delete(self):
        resolved = resolve('/admin/projects/3/subsets/5/delete/')
        self.assertEqual(resolved.func.__name__, SubsetDelete.__name__)
        self.assertEqual(resolved.kwargs['project_id'], '3')
        self.assertEqual(resolved.kwargs['subset_id'], '5')

    def test_reverse_subset_data(self):
        self.assertEqual(
            reverse('admin:subset_data', args=(3, 5, )),
            '/admin/projects/3/subsets/5/data/'
        )

    def test_resolve_subset_data(self):
        resolved = resolve('/admin/projects/3/subsets/5/data/')
        self.assertEqual(resolved.func.__name__, SubsetData.__name__)
        self.assertEqual(resolved.kwargs['project_id'], '3')
        self.assertEqual(resolved.kwargs['subset_id'], '5')
