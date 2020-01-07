from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from .utils import get_date_from_string
from .models import League, Match, MatchStats, Team
from .forms import (LeagueForm, LeadueMergeForm, LeaguesDeleteForm, LeaguesConfirmForm,
                    TeamForm, TeamMergeForm, TeamsDeleteForm, TeamsConfirmForm,
                   )
from .serializers import SeasonSerializer, MatchSerializer, MatchStatsSerializer



####################################################
#  League
####################################################
class LeagueUpdateView(BSModalUpdateView):
    model = League
    template_name = "core/update_league.html"
    form_class = LeagueForm
    success_message = "Success: League was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                self.object.api_update(slug=cleaned_data["slug"], 
                                        name=cleaned_data["name"], 
                                        team_type=cleaned_data["team_type"], 
                                        country=cleaned_data["country"], 
                                        load_status=cleaned_data["load_status"], 
                                        load_source=cleaned_data["load_source"]
                                        )
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class LeagueMergeView(BSModalUpdateView):
    model = League
    template_name = "core/merge_league.html"
    form_class = LeadueMergeForm
    success_message = "Success: League was merged to %(id)s."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, league_id):
        return self.success_message % {"id":league_id,}

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                league_id = cleaned_data["league_id"]
                self.object.api_merge_to(league_id)
                messages.success(self.request, self.get_success_message(league_id))
            except Exception as e:
                messages.error(self.request, "Merging error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class LeaguesDeleteView(generic.TemplateView):
    form_class = LeaguesDeleteForm
    success_message = "Success: %(cnt)s leagues were deleted."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LeaguesDeleteView, self).get_context_data(**kwargs)

        leagues_id = self.request.GET.get("leagues", None)
        if leagues_id:
            context["leagues_id"] = leagues_id

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                leagues_id = cleaned_data["leagues_id"]
                League.api_delete_leagues(leagues_id)
                cnt = len(leagues_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class LeaguesConfirmView(BSModalCreateView):
    # model = League
    form_class = LeaguesConfirmForm
    template_name = "football/confirm_leagues.html"
    success_message = "Success: %(cnt)s leagues were confirmed."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LeaguesConfirmView, self).get_context_data(**kwargs)

        leagues_id = self.request.GET.get("leagues", None)
        if leagues_id:
            context["leagues_id"] = leagues_id

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                leagues_id = cleaned_data["leagues_id"]
                load_source = cleaned_data["load_source"]
                League.api_confirm_leagues(leagues_id, load_source)
                cnt = len(leagues_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Confirming error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



####################################################
#  Season
####################################################

class SeasonAPI(ListAPIView):
    serializer_class = SeasonSerializer
    # queryset = FootballLeague.objects.all()
    lookup_field = "pk"

    def get_queryset(self, queryset, *args, **kwargs):
        # queryset = FootballLeague.objects.all()
        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(start_date__lte=date_to)
        selected_league_id = self.request.query_params.get("selected_league", None)
        if selected_league_id and int(selected_league_id) > 0:
            queryset = queryset.filter(league=selected_league_id)

        return queryset


####################################################
#  Match
####################################################
class MatchAPI(ListAPIView):
    serializer_class = MatchSerializer
    lookup_field = "pk"

    def get_queryset(self, queryset, *args, **kwargs):
        # queryset = FootballLeague.objects.all()
        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(match_date__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(match_date__lte=date_to)
        selected_league_id = self.request.query_params.get("selected_league", None)
        if selected_league_id and int(selected_league_id) > 0:
            queryset = queryset.filter(league=selected_league_id)
        season_id = self.request.query_params.get("season_id", None)
        if season_id and int(season_id) > 0:
            queryset = queryset.filter(season=season_id)

        return queryset


class MatchDetailView(generic.DetailView):
    model = Match
    template_name = "core/match_detail.html"


####################################################
#  MatchStats
####################################################
class MatchStatsAPI(ListAPIView):
    serializer_class = MatchStatsSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = MatchStats.objects.all()
        match_id = self.request.query_params.get("match_id", None)
        print("!!!!", match_id)
        if match_id and int(match_id) > 0:
            queryset = queryset.filter(match=match_id)

        return queryset


####################################################
#  Team
####################################################
class TeamUpdateView(BSModalUpdateView):
    model = Team
    template_name = "core/update_team.html"
    form_class = TeamForm
    success_message = "Success: Team was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                self.object.api_update(slug=cleaned_data["slug"], 
                                        name=cleaned_data["name"], 
                                        team_type=cleaned_data["team_type"], 
                                        country=cleaned_data["country"], 
                                        load_status=cleaned_data["load_status"], 
                                        load_source=cleaned_data["load_source"]
                                        )
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class TeamMergeView(BSModalUpdateView):
    model = Team
    template_name = "core/merge_team.html"
    form_class = TeamMergeForm
    success_message = "Success: Team was merged to %(id)s."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, team_id):
        return self.success_message % {"id":team_id,}

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                team_id = cleaned_data["team_id"]
                self.object.api_merge_to(team_id)
                messages.success(self.request, self.get_success_message(team_id))
            except Exception as e:
                messages.error(self.request, "Merging error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class TeamsDeleteView(generic.TemplateView):
    form_class = TeamsDeleteForm
    success_message = "Success: %(cnt)s teams were deleted."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TeamsDeleteView, self).get_context_data(**kwargs)

        teams_id = self.request.GET.get("teams", None)
        if teams_id:
            context["teams_id"] = teams_id
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                teams_id = cleaned_data["teams_id"]
                Team.api_delete_teams(teams_id)
                cnt = len(teams_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class TeamsConfirmView(BSModalCreateView):
    form_class = TeamsConfirmForm
    success_message = "Success: %(cnt)s teams were confirmed."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TeamsConfirmView, self).get_context_data(**kwargs)

        teams_id = self.request.GET.get("teams", None)
        if teams_id:
            context["teams_id"] = teams_id
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                teams_id = cleaned_data["teams_id"]
                load_source = cleaned_data["load_source"]
                Team.api_confirm_teams(teams_id, load_source)
                cnt = len(teams_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Confirming error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())
