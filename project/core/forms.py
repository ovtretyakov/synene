from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from bootstrap_modal_forms.forms import BSModalForm

from .models import League, Team, Referee, Season

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
        model = League
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        leagues_id = cleaned_data.get("leagues_id")
        if not leagues_id:
            raise ValidationError(_("No leagues to delete"))


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



######################################################################
class TeamForm(BSModalForm):

    class Meta:
        model = Team
        fields = ["slug", "name", "team_type", "country", "load_status", "load_source",]

######################################################################
class TeamMergeForm(BSModalForm):

    team_id = forms.IntegerField()

    class Meta:
        model = Team
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        team_id = cleaned_data.get("team_id")
        if not team_id:
            raise ValidationError(_("Choose team to merge"))

######################################################################
class TeamsDeleteForm(BSModalForm):

    teams_id = forms.CharField()

    class Meta:
        model = Team
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        teams_id = cleaned_data.get("teams_id")
        if not teams_id:
            raise ValidationError(_("No teams to delete"))

######################################################################
class TeamsConfirmForm(BSModalForm):

    teams_id = forms.CharField()

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
        teams_id = cleaned_data.get("teams_id")
        if not teams_id:
            raise ValidationError(_("No teams to confirm"))



######################################################################
class RefereeForm(BSModalForm):

    class Meta:
        model = Referee
        fields = ["slug", "name", "country", "load_status", "load_source",]

######################################################################
class RefereeMergeForm(BSModalForm):

    referee_id = forms.IntegerField()

    class Meta:
        model = Referee
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        referee_id = cleaned_data.get("referee_id")
        if not referee_id:
            raise ValidationError(_("Choose referee to merge"))

######################################################################
class RefereesDeleteForm(BSModalForm):

    referees_id = forms.CharField()

    class Meta:
        model = Referee
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        rferees_id = cleaned_data.get("rferees_id")
        if not rferees_id:
            raise ValidationError(_("No referees to delete"))

######################################################################
class RefereesConfirmForm(BSModalForm):

    referees_id = forms.CharField()

    class Meta:
        model = Referee
        fields = ["load_source",]

    def clean_load_source(self):
        load_source = self.cleaned_data["load_source"]
        if not load_source:
            raise ValidationError(_("No data source specified"))
        return load_source
    def clean(self):
        cleaned_data = super().clean()
        referees_id = cleaned_data.get("referees_id")
        if not referees_id:
            raise ValidationError(_("No referees to confirm"))


######################################################################
class SeasonForm(BSModalForm):
    class Meta:
        model = Season
        fields = ["name", "league", "start_date", "end_date", "load_source",]
