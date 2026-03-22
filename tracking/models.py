from django.conf import settings
from django.db import models


class TrackingNumber(models.Model):
    code = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    @property
    def latest_event(self):
        return self.events.order_by("-event_time").first()


class TrackingEvent(models.Model):
    tracking = models.ForeignKey(
        TrackingNumber, on_delete=models.CASCADE, related_name="events"
    )
    status = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    details = models.TextField(blank=True)
    event_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_time", "-id"]

    def __str__(self):
        return f"{self.tracking.code} - {self.status}"


class AdminAuditLog(models.Model):
    ACTION_CHOICES = [
        ("create_tracking", "Create Tracking"),
        ("update_tracking", "Update Tracking"),
        ("delete_tracking", "Delete Tracking"),
        ("add_event", "Add Event"),
        ("update_event", "Update Event"),
        ("delete_event", "Delete Event"),
        ("login", "Login"),
        ("logout", "Logout"),
    ]

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    action = models.CharField(max_length=40, choices=ACTION_CHOICES)
    tracking = models.ForeignKey(
        TrackingNumber, on_delete=models.SET_NULL, null=True, blank=True
    )
    event = models.ForeignKey(
        TrackingEvent, on_delete=models.SET_NULL, null=True, blank=True
    )
    message = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.admin_user} - {self.action}"
