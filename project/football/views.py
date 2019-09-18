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
from project.core.models import Sport, LoadSource, Season
from project.core.views import (LeagueMergeView, LeaguesDeleteView, LeaguesConfirmView,
                                SeasonView, SeasonAPI,
                                )
from .models import FootballLeague
from .serializers import   (FootballLeagueSerializer, 
                            )



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

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_source = self.request.GET.get("source", None)
        if selected_source:
            context["selected_source"] = int(selected_source)

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
class FootballSeasonView(SeasonView):
    template_name = "football/season_list.html"

    def get_leagues(self):
        return FootballLeague.objects.select_related("country").all().order_by("country__name", "pk")

class FootballSeasonAPI(SeasonAPI):
    def get_queryset(self, *args, **kwargs):
        queryset = Season.objects.filter(league__sport__slug=Sport.FOOTBALL)
        return super().get_queryset(queryset, *args, **kwargs)
