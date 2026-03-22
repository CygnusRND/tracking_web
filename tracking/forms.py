from django import forms

from .models import TrackingEvent, TrackingNumber


class TrackingSearchForm(forms.Form):
    code = forms.CharField(
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter tracking number",
                "class": "text-input",
                "autocomplete": "off",
            }
        ),
    )

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()


class TrackingNumberForm(forms.ModelForm):
    class Meta:
        model = TrackingNumber
        fields = ["code", "description"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "text-input"}),
            "description": forms.TextInput(attrs={"class": "text-input"}),
        }


class TrackingEventForm(forms.ModelForm):
    class Meta:
        model = TrackingEvent
        fields = ["status", "location", "details", "event_time"]
        widgets = {
            "status": forms.TextInput(attrs={"class": "text-input"}),
            "location": forms.TextInput(attrs={"class": "text-input"}),
            "details": forms.Textarea(attrs={"class": "text-area", "rows": 3}),
            "event_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "text-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_time"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["event_time"].required = False
