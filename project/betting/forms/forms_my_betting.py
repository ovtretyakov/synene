from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from bootstrap_modal_forms.forms import BSModalForm

from ..models import Odd, Forecast, Bet


######################################################################
class PickOddsForm(BSModalForm):

    odds_id = forms.CharField()

    class Meta:
        model = Forecast
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        odds_id = cleaned_data.get("odds_id")
        if not odds_id:
            raise ValidationError(_("No odds to select"))
    def save(self):
        None

######################################################################
class DeselectOddForm(BSModalForm):

    class Meta:
        model = Odd
        fields = [] 

    def save(self):
        None

######################################################################
class BetForm(BSModalForm):

    class Meta:
        model = Bet
        fields = [] 

    def save(self):
        None
