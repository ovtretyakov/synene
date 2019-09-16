from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from bootstrap_modal_forms.forms import BSModalForm

from .models import League

######################################################################
class LeagueForm(BSModalForm):

    class Meta:
        model = League
        fields = ["slug", "name", "team_type", "country", "load_status", "load_source",]

######################################################################
class LeadueMergeForm(BSModalForm):

    league_id = forms.IntegerField()

    class Meta:
        model = League
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        league_id = cleaned_data.get("league_id")
        if not league_id:
            raise ValidationError(_("Choose league to merge"))

######################################################################
class LeaguesDeleteForm(BSModalForm):

    leagues_id = forms.CharField()

    class Meta:
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        leagues_id = cleaned_data.get("leagues_id")
        if not league_id:
            raise ValidationError(_("No leagues to merge"))


######################################################################
class LeaguesConfirmForm(BSModalForm):

    leagues_id = forms.CharField()
    # load_source = forms.ModelChoiceField(queryset=League.objects.all())

    class Meta:
        model = League
        fields = ["load_source",]

    def clean_load_source(self):
        load_source = self.cleaned_data["load_source"]
        if not load_source:
            raise ValidationError(_("No data source specified"))
        return load_source
    def clean(self):
        cleaned_data = super().clean()
        leagues_id = cleaned_data.get("leagues_id")
        if not leagues_id:
            raise ValidationError(_("No leagues to confirm"))


