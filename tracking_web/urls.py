from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from tracking import views as tracking_views


urlpatterns = [
    path("", tracking_views.home, name="home"),
    path("track/", include("tracking.urls")),
    path("admin/", include("dashboard.urls")),
    path("auth/", include("tracking_web.two_factor_urls")),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("django-admin/", admin.site.urls),
]
