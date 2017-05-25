from django.test import TestCase

from django.utils import timezone

from geokey.socialinteractions.utils import (
    start2pull,
    check_dates,
    create_new_observation,
    get_category_and_field,
    pull_from_social_media
)

from datetime import timedelta


class CheckDatesTest(TestCase):
    """Test for 'check_dates'."""

    def test_method(self):
        """Test method."""

        now = timezone.now()
        updated_at = now - timedelta(minutes=10)

        print "now", now
        print "updated_at", updated_at

        value_true = check_dates(updated_at, '5min')

        self.assertEqual(True, value_true)

        value_false = check_dates(updated_at, 'daily')

        self.assertNotEqual(True, value_false)
