from django.test import TestCase
from django.utils import timezone

from .models import TrackingEvent, TrackingNumber


class TrackingTests(TestCase):
    def test_latest_event(self):
        tracking = TrackingNumber.objects.create(code="ABC123")
        TrackingEvent.objects.create(
            tracking=tracking,
            status="Created",
            event_time=timezone.now(),
        )
        latest = tracking.latest_event
        self.assertEqual(latest.status, "Created")
