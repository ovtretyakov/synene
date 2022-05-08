import logging
import traceback
from datetime import datetime, date, timedelta

from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import sql, F, Q, Count, Max

from graphos.sources.model import ModelDataSource
from graphos.renderers import gchart

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from .utils import get_date_from_string
from .models import League, Match, MatchStats, Team, Referee
from .forms import (LeagueForm, LeadueMergeForm, LeaguesDeleteForm, LeaguesConfirmForm,
                    TeamForm, TeamMergeForm, TeamsDeleteForm, TeamsConfirmForm,
                    RefereeForm, RefereeMergeForm, RefereesDeleteForm, RefereesConfirmForm,
                   )
from .serializers import SeasonSerializer, MatchSerializer, MatchStatsSerializer

from project.betting.models import Saldo


logger = logging.getLogger(__name__)


####################################################
#  Home
####################################################
class HomeView(generic.TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        d = date(2022, 4, 8)
        queryset = Saldo.objects.filter(saldo_date__gte=d).annotate(real_saldo=F("saldo_amt") + F("unsettled_amt")).order_by("saldo_date")

        fields = ["saldo_date", "real_saldo"]
        headers = ["Date", "Saldo"]
        options={'title': "My Saldo",
                 'colors': ['blue', ],
                 'chartArea':{'left':50,'width':'75%',}
                 }
        chart_width = 650
        saldo_chart = gchart.LineChart(ModelDataSource(queryset= queryset, 
                                                       fields=fields,
                                                       headers=headers,
                                                       ),
                                       options=options
                                       )
        saldo_chart.width = chart_width
        context["saldo_chart"] = saldo_chart

        return context    




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

class LeaguesDeleteView(BSModalCreateView):
    form_class = LeaguesDeleteForm
    template_name = "football/delete_leagues.html"
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
        referee_id = self.request.query_params.get("referee_id", None)
        if referee_id and int(referee_id) > 0:
            queryset = queryset.filter(matchreferee__referee__pk=referee_id)

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
                # logger.error(e) 
                logger.error(traceback.format_exc())
                messages.error(self.request, "Merging error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class TeamsDeleteView(BSModalCreateView):
    model = Team
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

####################################################
#  Referee
####################################################
class RefereeUpdateView(BSModalUpdateView):
    model = Referee
    template_name = "core/update_referee.html"
    form_class = RefereeForm
    success_message = "Success: Referee was updated."

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
                                        country=cleaned_data["country"], 
                                        load_status=cleaned_data["load_status"], 
                                        load_source=cleaned_data["load_source"]
                                        )
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class RefereeMergeView(BSModalUpdateView):
    model = Referee
    template_name = "core/merge_referee.html"
    form_class = RefereeMergeForm
    success_message = "Success: Referee was merged to %(id)s."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, referee_id):
        return self.success_message % {"id":referee_id,}

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                referee_id = cleaned_data["referee_id"]
                self.object.api_merge_to(referee_id)
                messages.success(self.request, self.get_success_message(referee_id))
            except Exception as e:
                # logger.error(e) 
                logger.error(traceback.format_exc())
                messages.error(self.request, "Merging error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class RefereesDeleteView(BSModalCreateView):
    model = Referee
    form_class = RefereesDeleteForm
    success_message = "Success: %(cnt)s referees were deleted."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(RefereesDeleteView, self).get_context_data(**kwargs)

        referees_id = self.request.GET.get("referees", None)
        if referees_id:
            context["referees_id"] = referees_id
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                referees_id = cleaned_data["referees_id"]
                Referee.api_delete_referees(referees_id)
                cnt = len(referees_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class RefereesConfirmView(BSModalCreateView):
    form_class = RefereesConfirmForm
    success_message = "Success: %(cnt)s referees were confirmed."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(RefereesConfirmView, self).get_context_data(**kwargs)

        referees_id = self.request.GET.get("referees", None)
        if referees_id:
            context["referees_id"] = referees_id
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                referees_id = cleaned_data["referees_id"]
                load_source = cleaned_data["load_source"]
                Referee.api_confirm_referees(referees_id, load_source)
                cnt = len(referees_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Confirming error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())





