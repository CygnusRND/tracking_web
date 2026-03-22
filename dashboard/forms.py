from django import forms

from tracking.forms import TrackingEventForm, TrackingNumberForm


class AdminTrackingNumberForm(TrackingNumberForm):
    pass


class AdminTrackingEventForm(TrackingEventForm):
    pass


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "text-input", "placeholder": "Search"}),
    )
