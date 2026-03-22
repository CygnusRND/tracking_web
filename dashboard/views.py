from django.contrib.auth.decorators import login_required, user_passes_test
from django_otp import user_has_device
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from tracking.models import AdminAuditLog, TrackingEvent, TrackingNumber
from tracking.services import log_admin_action
from .forms import AdminTrackingEventForm, AdminTrackingNumberForm, SearchForm


def staff_required(user):
    return user.is_authenticated and user.is_staff


def staff_view(view_func):
    secured = login_required(user_passes_test(staff_required)(view_func))

    def wrapped(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and not user.is_verified():
            if not user_has_device(user):
                return redirect("two_factor:setup")
            return redirect("two_factor:login")
        return secured(request, *args, **kwargs)

    return wrapped


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@staff_view
def dashboard_home(request):
    tracking_count = TrackingNumber.objects.count()
    event_count = TrackingEvent.objects.count()
    latest_events = TrackingEvent.objects.select_related("tracking")[:5]
    return render(
        request,
        "dashboard/home.html",
        {
            "tracking_count": tracking_count,
            "event_count": event_count,
            "latest_events": latest_events,
        },
    )


@staff_view
def tracking_list(request):
    form = SearchForm(request.GET)
    tracking_items = TrackingNumber.objects.all().order_by("-created_at")
    if form.is_valid():
        query = form.cleaned_data.get("query")
        if query:
            tracking_items = tracking_items.filter(
                Q(code__icontains=query) | Q(description__icontains=query)
            )
    return render(
        request,
        "dashboard/tracking_list.html",
        {"tracking_items": tracking_items, "form": form},
    )


@staff_view
def tracking_create(request):
    form = AdminTrackingNumberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        tracking = form.save(commit=False)
        tracking.code = tracking.code.strip().upper()
        tracking.created_by = request.user
        tracking.save()
        log_admin_action(
            request.user,
            "create_tracking",
            tracking=tracking,
            message="Tracking number created",
            ip_address=client_ip(request),
        )
        return redirect("dashboard:tracking_list")
    return render(request, "dashboard/tracking_form.html", {"form": form})


@staff_view
def tracking_edit(request, pk):
    tracking = get_object_or_404(TrackingNumber, pk=pk)
    form = AdminTrackingNumberForm(request.POST or None, instance=tracking)
    if request.method == "POST" and form.is_valid():
        tracking = form.save(commit=False)
        tracking.code = tracking.code.strip().upper()
        tracking.save()
        log_admin_action(
            request.user,
            "update_tracking",
            tracking=tracking,
            message="Tracking number updated",
            ip_address=client_ip(request),
        )
        return redirect("dashboard:tracking_list")
    return render(
        request, "dashboard/tracking_form.html", {"form": form, "tracking": tracking}
    )


@staff_view
@require_http_methods(["POST", "GET"])
def tracking_delete(request, pk):
    tracking = get_object_or_404(TrackingNumber, pk=pk)
    if request.method == "POST":
        log_admin_action(
            request.user,
            "delete_tracking",
            tracking=tracking,
            message="Tracking number deleted",
            ip_address=client_ip(request),
        )
        tracking.delete()
        return redirect("dashboard:tracking_list")
    return render(request, "dashboard/tracking_delete.html", {"tracking": tracking})


@staff_view
def event_create(request, pk):
    tracking = get_object_or_404(TrackingNumber, pk=pk)
    form = AdminTrackingEventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.tracking = tracking
        if not event.event_time:
            event.event_time = timezone.now()
        event.save()
        log_admin_action(
            request.user,
            "add_event",
            tracking=tracking,
            event=event,
            message="Tracking event added",
            ip_address=client_ip(request),
        )
        return redirect("dashboard:tracking_edit", pk=tracking.pk)
    return render(
        request, "dashboard/event_form.html", {"form": form, "tracking": tracking}
    )


@staff_view
def event_edit(request, pk, event_id):
    tracking = get_object_or_404(TrackingNumber, pk=pk)
    event = get_object_or_404(TrackingEvent, pk=event_id, tracking=tracking)
    form = AdminTrackingEventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        log_admin_action(
            request.user,
            "update_event",
            tracking=tracking,
            event=event,
            message="Tracking event updated",
            ip_address=client_ip(request),
        )
        return redirect("dashboard:tracking_edit", pk=tracking.pk)
    return render(
        request,
        "dashboard/event_form.html",
        {"form": form, "tracking": tracking, "event": event},
    )


@staff_view
@require_http_methods(["POST", "GET"])
def event_delete(request, pk, event_id):
    tracking = get_object_or_404(TrackingNumber, pk=pk)
    event = get_object_or_404(TrackingEvent, pk=event_id, tracking=tracking)
    if request.method == "POST":
        log_admin_action(
            request.user,
            "delete_event",
            tracking=tracking,
            event=event,
            message="Tracking event deleted",
            ip_address=client_ip(request),
        )
        event.delete()
        return redirect("dashboard:tracking_edit", pk=tracking.pk)
    return render(
        request,
        "dashboard/event_delete.html",
        {"tracking": tracking, "event": event},
    )


@staff_view
def audit_logs(request):
    logs = AdminAuditLog.objects.select_related("admin_user", "tracking", "event")[:200]
    return render(request, "dashboard/audit_logs.html", {"logs": logs})
