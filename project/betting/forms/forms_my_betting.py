from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from bootstrap_modal_forms.forms import BSModalForm

from ..models import Odd, Forecast, Bet, SelectedOdd, Transaction


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


######################################################################
class SelectedOddsForm(BSModalForm):

    hodd = forms.CharField(required=False)
    hmatch = forms.CharField(required=False)
    hleague = forms.CharField(required=False)
    selected_odds_id = forms.CharField()
    obj_type = forms.IntegerField()
    bookie = forms.CharField(required=False)
    show_hidden = forms.CharField(required=False)
    bid_matches = forms.CharField(required=False)

    class Meta:
        model = SelectedOdd
        fields = []

    # def clean(self):
    #     cleaned_data = super().clean()
    #     selected_odds_id = cleaned_data.get("selected_odds_id")
    #     if not selected_odds_id:
    #         raise ValidationError(_("No odds to deselect"))

######################################################################
class TransactionForm(BSModalForm):
    class Meta:
        model = Transaction
        fields = ["bookie", "trans_type", "trans_date", "amount", "comment",]

    def save(self):
        None

