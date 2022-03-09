from datetime import datetime, date, timedelta
from decimal import Decimal


from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.query import RawQuerySet
from django.db.models import sql, F, Q, Count, Max
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string, SimpleRawQuerySet

from project.core.models import Sport, League, Match, LoadSource, Team
from ..forms import PickOddsForm, DeselectOddForm, BetForm
from ..models import Odd, ForecastSandbox, SelectedOdd, Bet
from ..serializers import SelectedOddsSerializer


####################################################
#  PickOdd
####################################################
class PickOddsView(BSModalCreateView):
    form_class = PickOddsForm
    template_name = "betting/pick_odds.html"
    success_message = "Success: %(cnt)s odds were selected."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(PickOddsView, self).get_context_data(**kwargs)

        odds_id = self.request.GET.get("odds", None)
        if odds_id:
            odds = odds_id.split(",")
            odds_cnt = len(odds)
            context["odds_id"] = odds_id
            context["odds_cnt"] = odds_cnt

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                odds_id = cleaned_data["odds_id"]
                odds = odds_id.split(",")
                items = ForecastSandbox.objects.filter(id__in=odds).values()
                SelectedOdd.add(items)
                cnt = len(odds)
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Picking error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class DeselectOddView(BSModalUpdateView):
    model = Odd
    form_class = DeselectOddForm
    template_name = 'betting/deselect_odd.html'
    success_message = "Success: %(id)s odd was deselected."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, odd_cnt):
        return self.success_message % {"id":odd_cnt,}


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(DeselectOddView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        if pk:
            object = Odd.objects.get(pk=pk)
            context["object"] = object
        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                odd_id = self.object.id
                n = SelectedOdd.api_delete_odd(odd_id)
                messages.success(self.request, self.get_success_message(n))
            except Exception as e:
                messages.error(self.request, "Deselecting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  SelectedOdd
####################################################
class SelectedOddsView(generic.TemplateView):
    template_name = "betting/selected_odd_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(SelectedOddsView, self).get_context_data(**kwargs)

        return context    


class SelectedOddListAPI(ListAPIView):
    serializer_class = SelectedOddsSerializer
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):

        sql = """ 
                WITH s2 AS (
                  SELECT s.id AS select_id,
                         m.league_id, l.name AS legue_name,
                         s.match_id, h.name || ' - ' || a.name || ' ' || TO_CHAR(m.match_date,'DD.MM.YYYY') AS match_name, m.match_date,
                         s.success_chance, s.lose_chance, s.result_value, s.kelly,
                         s.odd_id, bt.name AS bet_type_name, o.odd_value, o.period, o.param, o.team, o.yes, o.selected,
                         b.name AS bookie_name, p.name AS predictor_name
                    FROM betting_selectedodd s
                    JOIN core_match m ON(s.match_id = m.id)
                    JOIN core_league l ON(m.league_id = l.id)
                    JOIN core_team h ON(m.team_h_id = h.id)
                    JOIN core_team a ON(m.team_a_id = a.id)
                    JOIN betting_odd o ON(s.odd_id = o.id)
                    JOIN betting_bettype bt ON(o.bet_type_id = bt.id)
                    JOIN core_loadsource b ON(o.bookie_id = b.id)
                    JOIN betting_predictor p ON(s.predictor_id = p.id)
                ),
                s3 AS (
                SELECT CASE WHEN match_id IS NULL AND select_id IS NULL THEN 1 ELSE 0 END AS league_grp, 
                       CASE WHEN select_id IS NULL THEN 1 ELSE 0 END AS match_grp, 
                       select_id,
                       league_id, legue_name || ' (' || COUNT(DISTINCT match_id) || ' matches)' AS legue_name, 
                       match_id, match_name || ' (' || COUNT(*) || ' odds)' AS match_name, 
                       match_date,
                       success_chance, lose_chance, result_value, kelly, odd_id, bet_type_name, odd_value, period, param, team, yes, selected,
                       bookie_name, predictor_name,
                       COUNT(DISTINCT match_id) AS match_cnt,
                       COUNT(*) AS odd_cnt
                  FROM s2
                  GROUP BY GROUPING SETS ((league_id, legue_name),
                                          (league_id, legue_name, match_id, match_name, match_date),
                                          (select_id, league_id, legue_name, match_id, match_name, match_date, success_chance, lose_chance, result_value, kelly,
                                           odd_id, bet_type_name, odd_value, period, param, team, yes, selected, bookie_name, predictor_name)
                                          )  
                ),
                s4 AS (
                  SELECT league_grp, match_grp, league_id, match_id, select_id,
                         CASE WHEN league_grp = 1 THEN league_id WHEN match_grp = 1 THEN match_id ELSE select_id END AS id,
                         CASE WHEN league_grp = 1 THEN legue_name WHEN match_grp = 1 THEN match_name ELSE bet_type_name END AS name,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE success_chance END AS success_chance,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE lose_chance END AS lose_chance,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE result_value END AS result_value,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE kelly END AS kelly,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE odd_id END AS odd_id,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE odd_value END AS odd_value,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE period END AS period,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE param END AS param,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE team END AS team,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE yes END AS yes,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE bookie_name END AS bookie_name,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE predictor_name END AS predictor_name,
                         CASE WHEN league_grp = 1 OR match_grp = 1 THEN NULL ELSE selected END AS selected
                  FROM s3
                ),
                s5 AS (
                SELECT s41.*,
                       MAX(bid0) OVER(PARTITION BY match_id) AS match_bid
                  FROM 
                    (
                      SELECT s4.*,
                             CASE WHEN match_grp=1 AND league_grp = 0 
                                  THEN COALESCE((SELECT MAX(CASE WHEN selected='b' THEN 1 ELSE 0 END) 
                                                   FROM betting_odd o 
                                                   WHERE o.match_id = s4.match_id 
                                                ),0) 
                                  ELSE 0 END AS bid0
                        FROM s4
                    ) s41
                )
                SELECT * FROM s5
                  ORDER BY league_id, league_grp DESC, match_id, match_grp DESC, select_id                        
              """
        params  = []      
        queryset = SimpleRawQuerySet(sql, params=params, model=SelectedOdd)
        return queryset


####################################################
#  Bet
####################################################
class CreateBetView(BSModalCreateView):
    model = Bet
    form_class = BetForm
    template_name = 'betting/create_bet.html'
    success_message = "Success: Bet was created."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(CreateBetView, self).get_context_data(**kwargs)
        odds_id = self.request.GET.get("odds", None)
        if odds_id:
            items = SelectedOdd.objects.filter(id__in=odds_id.split(",")).annotate(odd_name=F("odd__bet_type__name"),
                                                                                   odd_value=F("odd__odd_value"),
                                                                                   odd_param=F("odd__param"),
                                                                                   odd_team=F("odd__team"),
                                                                                   odd_period=F("odd__period"),
                                                                                   odd_yes=F("odd__yes"),
                                                                                   bookie_id=F("odd__bookie_id"),
                                                                                   bookie_name=F("odd__bookie__name"),
                                                                                   h_name=F("match__team_h__name"),
                                                                                   a_name=F("match__team_a__name"),
                                                                                   league_name=F("match__league__name"),
                                                                                   ).values()
            bookie_id = None
            bookie_name = None
            if len(items) > 0:
                bookie_id = items[0]["bookie_id"]
                bookie_name = items[0]["bookie_name"]
            context["odds_id"] = odds_id
            context["items"] = items
            context["bookie_id"] = bookie_id
            context["bookie_name"] = bookie_name


        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                bookie_id = int(self.request.POST.get('bookie_id'))
                bet_amt = Decimal(self.request.POST.get('bet_amt'))
                ids = self.request.POST.getlist('id')
                items = [{"odd_id":int(self.request.POST['odd_id-{}'.format(id)]),
                          "odd_name":self.request.POST['odd_name-{}'.format(id)],
                          "odd_value":Decimal(self.request.POST['odd_value-{}'.format(id)]),
                          "predictor_id":int(self.request.POST['predictor_id-{}'.format(id)]),
                          "result_value":Decimal(self.request.POST['result_value-{}'.format(id)]),
                          "match_id":int(self.request.POST['match_id-{}'.format(id)]),
                          "harvest_id":int(self.request.POST['harvest_id-{}'.format(id)]),
                          "success_chance":Decimal(self.request.POST['success_chance-{}'.format(id)]),
                          "lose_chance":Decimal(self.request.POST['lose_chance-{}'.format(id)]),
                          }for id in ids]
                bet = Bet.api_create(bookie_id, items, bet_amt)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Creating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



