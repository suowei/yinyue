from django import forms
from .models import City


class ShowForm(forms.Form):
    date = forms.DateField()
    city = forms.ModelChoiceField(required=False, queryset=City.objects.order_by('seq'))
