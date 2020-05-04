from django.shortcuts import render

from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string
from project.core.models import Sport, Country, LoadSource, Season, Match, TeamType
from project.core.views import (LeagueMergeView, LeaguesDeleteView, LeaguesConfirmView,
                                SeasonAPI,
                                MatchAPI,
                                TeamMergeView, TeamsDeleteView, TeamsConfirmView,
                                )
from project.core.mixins import LeagueGetContextMixin

from .models import FootballLeague, FootballTeam
from .serializers import FootballLeagueSerializer, FootballTeamSerializer



####################################################
#  FootballLeague
####################################################
class FootballLeagueView(generic.TemplateView):
    template_name = "football/league_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(FootballLeagueView, self).get_context_data(**kwargs)

        load_sources = LoadSource.objects.all().order_by("pk")
        context["sources"] = load_sources

        load_statuses = (("a", "All"),) + FootballLeague.STATUS_CHOICES
        context["statuses"] = load_statuses

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_source = self.request.GET.get("source", None)
        if selected_source:
            context["selected_source"] = int(selected_source)
        selected_status = self.request.GET.get("status", None)
        if selected_status:
            context["selected_status"] = selected_status
        else:
            context["selected_status"] = "a"

        return context    


class FootballLeagueAPI(ListAPIView):
    serializer_class = FootballLeagueSerializer
    # queryset = FootballLeague.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = FootballLeague.objects.all()
        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(created__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(created__lte=date_to)
        load_source_id = self.request.query_params.get("selected_source", None)
        if load_source_id and int(load_source_id) > 0:
            queryset = queryset.filter(load_source=load_source_id)
        selected_status = self.request.query_params.get("selected_status", None)
        if selected_status and selected_status != "a":
            queryset = queryset.filter(load_status=selected_status)
        leagues = self.request.query_params.get("leagues", None)
        if leagues:
            leagues_id = leagues.split(",")
            queryset = queryset.filter(pk__in=leagues_id)

        return queryset


class SelectFootballLeagueView(generic.TemplateView):
    template_name = "football/select_league.html"

class FootballLeagueMergeView(LeagueMergeView):
    template_name = "football/merge_league.html"

class FootballLeaguesDeleteView(LeaguesDeleteView):
    template_name = "football/delete_leagues.html"

class FootballLeaguesConfirmView(LeaguesConfirmView):
    template_name = "football/confirm_leagues.html"



####################################################
#  FootballSeason
####################################################
class FootballSeasonView(LeagueGetContextMixin, generic.TemplateView):
    template_name = "football/season_list.html"
    def get_leagues(self):
        return FootballLeague.objects.select_related("country").all().order_by("country__name", "pk")

class FootballSeasonAPI(SeasonAPI):
    def get_queryset(self, *args, **kwargs):
        queryset = Season.objects.filter(league__sport__slug=Sport.FOOTBALL)
        return super().get_queryset(queryset, *args, **kwargs)


####################################################
#  FootballMatch
####################################################
class FootballMatchView(LeagueGetContextMixin, generic.TemplateView):
    template_name = "football/match_list.html"
    def get_leagues(self):
        return FootballLeague.objects.select_related("country").all().order_by("country__name", "pk")

class FootballMatchAPI(MatchAPI):
    def get_queryset(self, *args, **kwargs):
        queryset = Match.objects.filter(league__sport__slug=Sport.FOOTBALL)
        return super().get_queryset(queryset, *args, **kwargs)


####################################################
#  FootballTeam
####################################################
class FootballTeamView(generic.TemplateView):
    template_name = "football/team_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(FootballTeamView, self).get_context_data(**kwargs)

        load_sources = LoadSource.objects.all().order_by("pk")
        context["sources"] = load_sources
        countries = Country.objects.all().order_by("name")
        context["countries"] = countries
        team_types = TeamType.objects.all().order_by("name")
        context["team_types"] = team_types

        load_statuses = FootballLeague.STATUS_CHOICES
        context["statuses"] = load_statuses

        selected_source = self.request.GET.get("source", None)
        if selected_source:
            context["selected_source"] = int(selected_source)
        selected_country = self.request.GET.get("country", None)
        if selected_country:
            context["selected_country"] = int(selected_country)
        selected_team_type = self.request.GET.get("team_type", None)
        if selected_team_type:
            context["selected_team_type"] = int(selected_team_type)

        selected_status = self.request.GET.get("status", None)
        if selected_status:
            context["selected_status"] = selected_status
        else:
            context["selected_status"] = "a"

        return context


class FootballTeamAPI(ListAPIView):
    serializer_class = FootballTeamSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = FootballTeam.objects.all()

        teams = self.request.query_params.get("teams", None)
        if teams:
            teams_id = teams.split(",")
            queryset = queryset.filter(pk__in=teams_id)

        load_source_id = self.request.query_params.get("selected_source", None)
        if load_source_id and int(load_source_id) > 0:
            queryset = queryset.filter(load_source=load_source_id)

        selected_status = self.request.query_params.get("selected_status", None)
        if selected_status and selected_status != "a":
            queryset = queryset.filter(load_status=selected_status)

        country_id = self.request.query_params.get("selected_country", None)
        if country_id and int(country_id) > 0:
            queryset = queryset.filter(country=country_id)

        team_type_id = self.request.query_params.get("selected_team_type", None)
        if team_type_id and int(team_type_id) > 0:
            queryset = queryset.filter(team_type=team_type_id)

        return queryset


class SelectFootballTeamView(generic.TemplateView):
    template_name = "football/select_team.html"

class FootballTeamMergeView(TeamMergeView):
    template_name = "football/merge_team.html"

class FootballTeamsDeleteView(TeamsDeleteView):
    template_name = "football/delete_teams.html"

class FootballTeamsConfirmView(TeamsConfirmView):
    template_name = "football/confirm_teams.html"
