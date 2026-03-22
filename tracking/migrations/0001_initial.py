from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TrackingNumber",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=32, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TrackingEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(max_length=120)),
                ("location", models.CharField(blank=True, max_length=120)),
                ("details", models.TextField(blank=True)),
                ("event_time", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tracking",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="tracking.trackingnumber"),
                ),
            ],
            options={"ordering": ["-event_time", "-id"]},
        ),
        migrations.CreateModel(
            name="AdminAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("create_tracking", "Create Tracking"),
                            ("update_tracking", "Update Tracking"),
                            ("delete_tracking", "Delete Tracking"),
                            ("add_event", "Add Event"),
                            ("update_event", "Update Event"),
                            ("delete_event", "Delete Event"),
                            ("login", "Login"),
                            ("logout", "Logout"),
                        ],
                        max_length=40,
                    ),
                ),
                ("message", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "admin_user",
                    models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "event",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="tracking.trackingevent"),
                ),
                (
                    "tracking",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="tracking.trackingnumber"),
                ),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
    ]
