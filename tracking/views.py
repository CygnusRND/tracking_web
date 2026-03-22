from django.shortcuts import get_object_or_404, redirect, render

from .forms import TrackingSearchForm
from .models import TrackingNumber


def home(request):
    form = TrackingSearchForm()
    if request.method == "POST":
        form = TrackingSearchForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            return redirect("tracking:detail", code=code)
    return render(request, "tracking/home.html", {"form": form})


def tracking_detail(request, code):
    tracking = get_object_or_404(TrackingNumber, code=code.upper())
    events = tracking.events.all()
    return render(
        request,
        "tracking/detail.html",
        {"tracking": tracking, "events": events, "latest": tracking.latest_event},
    )
