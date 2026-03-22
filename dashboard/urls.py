from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("tracking/", views.tracking_list, name="tracking_list"),
    path("tracking/new/", views.tracking_create, name="tracking_create"),
    path("tracking/<int:pk>/edit/", views.tracking_edit, name="tracking_edit"),
    path("tracking/<int:pk>/delete/", views.tracking_delete, name="tracking_delete"),
    path("tracking/<int:pk>/events/new/", views.event_create, name="event_create"),
    path("tracking/<int:pk>/events/<int:event_id>/edit/", views.event_edit, name="event_edit"),
    path("tracking/<int:pk>/events/<int:event_id>/delete/", views.event_delete, name="event_delete"),
    path("logs/", views.audit_logs, name="audit_logs"),
]
