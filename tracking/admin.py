from django.contrib import admin

from .models import AdminAuditLog, TrackingEvent, TrackingNumber


@admin.register(TrackingNumber)
class TrackingNumberAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "created_at", "updated_at")
    search_fields = ("code", "description")


@admin.register(TrackingEvent)
class TrackingEventAdmin(admin.ModelAdmin):
    list_display = ("tracking", "status", "location", "event_time")
    search_fields = ("tracking__code", "status", "location")


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("admin_user", "action", "tracking", "event", "created_at")
    search_fields = ("admin_user__username", "tracking__code", "action")
