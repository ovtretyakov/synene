from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string
from project.core.models import LoadSource
from project.football.models import FootballLeague
from .models import Odd, VOdd, ValueType, BetType, Match
from .serializers import OddSerializer



####################################################
#  Odd
####################################################
class OddView(generic.TemplateView):
    template_name = "betting/odd_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(OddView, self).get_context_data(**kwargs)


        context["results"] = (("a", "All results"),) + Odd.RESULT_CHOICES
        context["leagues"] = FootballLeague.objects.select_related("country").all().order_by("country__name", "pk")
        context["sources"] = LoadSource.objects.all().order_by("pk")
        context["sections"] = ValueType.objects.all().order_by("name")
        context["types"] = BetType.objects.all().order_by("name")


        match_id = self.request.GET.get("match_id", None)
        match = None
        if match_id and int(match_id) > 0:
            try:
                match = Match.objects.get(pk=match_id)
                context["match_id"] = match_id
                context["match_name"] = match.team_h.name + " - " + match.team_a.name
                context["match_date"] = match.match_date.strftime('%d.%m.%Y')
                context["date_to_disabled"] = "disabled"
                context["date_from_disabled"] = "disabled"
                context["league_disabled"] = "disabled"
            except Match.DoesNotExist:
                match = None

        if not match:
            date_to = self.request.GET.get("date_to", None)
            if date_to:
                context["date_to"] = date_to
            date_from = self.request.GET.get("date_from", None)
            if date_from:
                context["date_from"] = date_from
            selected_league = self.request.GET.get("selected_league", None)
            if selected_league:
                context["selected_league"] = int(selected_league)
        selected_bookie = self.request.GET.get("bookie", None)
        if selected_bookie:
            context["selected_bookie"] = int(selected_bookie)
        selected_section = self.request.GET.get("section", None)
        if selected_section:
            context["selected_section"] = int(selected_section)
        selected_type = self.request.GET.get("type", None)
        if selected_type:
            context["selected_type"] = int(selected_type)
        per = self.request.GET.get("per", None)
        if per:
            context["per"] = per
        odd_from = self.request.GET.get("odd_from", None)
        if odd_from:
            context["odd_from"] = odd_from
        odd_to = self.request.GET.get("odd_to", None)
        if odd_to:
            context["odd_to"] = odd_to
        selected_team = self.request.GET.get("team", None)
        if selected_team:
            context["selected_team"] = selected_team
        else:
            context["selected_team"] = "all"
        par = self.request.GET.get("par", None)
        if par:
            context["par"] = par
        selected_result = self.request.GET.get("result", None)
        if selected_result:
            context["selected_result"] = selected_result
        else:
            context["selected_result"] = "a"


        # selected_status = self.request.GET.get("status", None)
        # if selected_status:
        #     context["selected_status"] = selected_status
        # else:
        #     context["selected_status"] = "a"

        return context    


class OddAPI(ListAPIView):
    serializer_class = OddSerializer
    # queryset = Odd.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = VOdd.objects.all()
        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(match_date__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(match_date__lte=date_to)
        selected_league_id = self.request.query_params.get("selected_league", None)
        if selected_league_id and int(selected_league_id) > 0:
            queryset = queryset.filter(league_id=selected_league_id)
        selected_bookie = self.request.query_params.get("selected_bookie", None)
        if selected_bookie and int(selected_bookie) > 0:
            queryset = queryset.filter(bookie_id=selected_bookie)
        selected_section = self.request.query_params.get("selected_section", None)
        if selected_section and int(selected_section) > 0:
            queryset = queryset.filter(value_type_id=selected_section)
        selected_type = self.request.query_params.get("selected_type", None)
        if selected_type and int(selected_type) > 0:
            queryset = queryset.filter(bet_type_id=selected_type)
        per = self.request.query_params.get("per", None)
        if per:
            queryset = queryset.filter(period=per)
        odd_from = self.request.query_params.get("odd_from", None)
        if odd_from:
            queryset = queryset.filter(odd_value__gte=odd_from)
        odd_to = self.request.query_params.get("odd_to", None)
        if odd_to:
            queryset = queryset.filter(odd_value__lte=odd_to)
        selected_team = self.request.query_params.get("selected_team", None)
        if selected_team:
            if selected_team in("h","a"):
                queryset = queryset.filter(team=selected_team)
            elif selected_team == "empty":
                queryset = queryset.filter(team="")
        par = self.request.query_params.get("par", None)
        if par:
            queryset = queryset.filter(param=par)
        selected_result = self.request.query_params.get("selected_result", None)
        if selected_result and selected_result != "a":
            queryset = queryset.filter(result=selected_result)

        match_id = self.request.query_params.get("match_id", None)
        if match_id and int(match_id) > 0:
            queryset = queryset.filter(match_id=match_id)

        return queryset
