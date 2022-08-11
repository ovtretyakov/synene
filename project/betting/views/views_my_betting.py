from datetime import datetime, date, timedelta
from decimal import Decimal


from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.query import RawQuerySet
from django.db.models import sql, F, Q, Count, Max, Value as V
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber, Concat

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string, SimpleRawQuerySet

from project.core.models import Sport, League, Match, LoadSource, Team
from ..forms import PickOddsForm, DeselectOddForm, BetForm, SelectedOddsForm, TransactionForm
from ..models import Odd, ForecastSandbox, SelectedOdd, Bet, BetOdd, Transaction
from ..serializers import SelectedOddsSerializer, MyBetSerializer, TransactionSerializer, BetOddSerializer


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
        hodd = self.request.GET.get("hodd", "")
        hmatch = self.request.GET.get("hmatch", "")
        hleague = self.request.GET.get("hleague", "")
        context["hodd"] = hodd
        context["hmatch"] = hmatch
        context["hleague"] = hleague
        bookie = self.request.GET.get("bookie", "")
        show_hidden = self.request.GET.get("show_hidden", "")
        bid_matches = self.request.GET.get("bid_matches", "")
        context["bookie"] = bookie
        context["show_hidden"] = show_hidden
        context["bid_matches"] = bid_matches

        context["bookies"] = LoadSource.objects.filter(is_betting=True).order_by("pk")
        selected_bookie = self.request.GET.get("bookie", None)
        if selected_bookie:
            context["selected_bookie"] = int(selected_bookie)

        return context    


class SelectedOddListAPI(ListAPIView):
    serializer_class = SelectedOddsSerializer
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):

        hodd_condition = ""
        hmatch_condition = ""
        hleague_condition = ""

        show_hidden = self.request.query_params.get("show_hidden", "")
        if show_hidden != "y":
            hodd = self.request.query_params.get("hodd", None)
            if hodd:
                hodd_condition = f" AND s.id NOT IN({hodd})"
            hmatch = self.request.query_params.get("hmatch", None)
            if hmatch:
                hmatch_condition = f" AND s.match_id NOT IN({hmatch})"
            hleague = self.request.query_params.get("hleague", None)
            if hleague:
                hleague_condition = f" AND m.league_id NOT IN({hleague})"

        bid_matches = self.request.query_params.get("bid_matches", "")
        bid_matches_condition = ""
        if bid_matches != "s":
            bid_matches_condition = " AND match_bid=0 "


        sql = f""" 
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
                    WHERE 1=1
                      {hodd_condition}
                      {hmatch_condition}
                      {hleague_condition}
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
                  WHERE 1=1
                  {bid_matches_condition}
                  ORDER BY league_id, league_grp DESC, match_id, match_grp DESC, kelly DESC, result_value DESC, select_id                        
              """
        params  = []      
        queryset = SimpleRawQuerySet(sql, params=params, model=SelectedOdd)
        return queryset

class SelectedOddsDeleteView(BSModalCreateView):
    model = SelectedOdd
    form_class = SelectedOddsForm
    success_message = "Success: %(cnt)s odds were deselected."
    template_name = 'betting/delete_selected_odds.html'
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(SelectedOddsDeleteView, self).get_context_data(**kwargs)

        selected_odds_id = self.request.GET.get("odds", None)
        obj_type = self.request.GET.get("type", None)
        context["action"] = "Erase"
        if not obj_type:
            obj_type = "0"
        if selected_odds_id:
            context["obj_type"] = obj_type
            context["selected_odds_id"] = selected_odds_id
            info = ""
            if obj_type == "1":
                info = "Are you sure to erase all match odds?"
            elif obj_type == "2":
                info = "Are you sure to erase all league odds?"
            elif selected_odds_id == "all":
                info = "Are you sure to erase all odds?"
            else:
                cnt = len(selected_odds_id.split(","))
                info = f'Are you sure to erase {cnt} odds?'
            context["info"] = info
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                selected_odds_id = cleaned_data["selected_odds_id"]
                obj_type = int(cleaned_data["obj_type"])
                cnt = 0
                if selected_odds_id == "all":
                    cnt = SelectedOdd.api_delete_all()
                else:
                    ids = selected_odds_id.split(",")
                    cnt = SelectedOdd.api_delete_by_idds(ids, obj_type)
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



class SelectedOddsHideView(BSModalCreateView):
    model = SelectedOdd
    form_class = SelectedOddsForm
    template_name = 'betting/delete_selected_odds.html'
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(SelectedOddsHideView, self).get_context_data(**kwargs)

        selected_odds_id = self.request.GET.get("odds", None)
        hodd = self.request.GET.get("hodd", "")
        hmatch = self.request.GET.get("hmatch", "")
        hleague = self.request.GET.get("hleague", "")
        obj_type = self.request.GET.get("type", None)

        bookie = self.request.GET.get("bookie", "")
        show_hidden = self.request.GET.get("show_hidden", "")
        bid_matches = self.request.GET.get("bid_matches", "")
        context["bookie"] = bookie
        context["show_hidden"] = show_hidden
        context["bid_matches"] = bid_matches
        if not obj_type:
            obj_type = "0"
        context["action"] = "Hide"
        if selected_odds_id:
            context["obj_type"] = obj_type
            context["selected_odds_id"] = selected_odds_id
            context["hodd"] = hodd
            context["hmatch"] = hmatch
            context["hleague"] = hleague
            info = ""
            if obj_type == "1":
                info = "Are you sure to hide all match odds?"
            elif obj_type == "2":
                info = "Are you sure to hide all league odds?"
            elif selected_odds_id == "all":
                info = "Are you sure to hide all odds?"
            else:
                cnt = len(selected_odds_id.split(","))
                info = f'Are you sure to hide {cnt} odds?'
            context["info"] = info
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            cleaned_data = form.cleaned_data
            selected_odds_id = cleaned_data["selected_odds_id"]
            obj_type = int(cleaned_data["obj_type"])

            bookie = cleaned_data["bookie"]
            show_hidden = cleaned_data["show_hidden"]
            bid_matches = cleaned_data["bid_matches"]

            hodd = cleaned_data["hodd"]
            hmatch = cleaned_data["hmatch"]
            hleague = cleaned_data["hleague"]
            ar_hodd = [] if not hodd else hodd.split(",")
            ar_hmatch = [] if not hmatch else hmatch.split(",")
            ar_hleague = [] if not hleague else hleague.split(",")

            ar_hide = [] if not selected_odds_id else selected_odds_id.split(",")

            for hide in ar_hide:
                if obj_type == 1:
                    if not hide in(ar_hmatch):
                        ar_hmatch.append(hide)
                elif obj_type == 2:
                    if not hide in(ar_hleague):
                        ar_hleague.append(hide)
                else:
                    if not hide in(ar_hodd):
                        print("add", hide)
                        ar_hodd.append(hide)

            url = reverse_lazy("betting:selected_odd_list")
            url += "?bookie=" + bookie
            url += "&show_hidden=" + show_hidden
            url += "&bid_matches=" + bid_matches
            url += "&hodd=" + ",".join([elem for elem in ar_hodd])
            url += "&hmatch=" + ",".join([elem for elem in ar_hmatch])
            url += "&hleague=" + ",".join([elem for elem in ar_hleague])
            return HttpResponseRedirect(url)
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  Bet
####################################################
class MyBetView(generic.TemplateView):
    template_name = "betting/my_bet_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(MyBetView, self).get_context_data(**kwargs)
        context["bookies"] = LoadSource.objects.filter(is_betting=True).order_by("pk")

        statuses = (("a", "All"),) + Bet.STATUS_CHOICES
        context["statuses"] = statuses

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if not date_from:
            date_from = (date.today() - timedelta(1)).strftime('%d.%m.%Y')
        context["date_from"] = date_from
        selected_bookie = self.request.GET.get("bookie", None)
        if selected_bookie:
            context["selected_bookie"] = int(selected_bookie)
        selected_status = self.request.GET.get("status", None)
        if selected_status:
            context["selected_status"] = selected_status
        else:
            context["selected_status"] = "a"

        return context    


class MyBetAPI(ListAPIView):
    serializer_class = MyBetSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = Bet.objects.all()

        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(ins_time__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(ins_time__lte=date_to)
        bookie = self.request.query_params.get("selected_bookie", None)
        if bookie and int(bookie) > 0:
            queryset = queryset.filter(bookie=bookie)
        status = self.request.query_params.get("selected_status", None)
        if status and status != "a":
            queryset = queryset.filter(status=status)

        return queryset

class MyBetDetail(BSModalReadView):
    model = Bet
    template_name = 'betting/my_bet_detail.html'


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
        action_type = self.request.GET.get("type", None)
        bet_id = self.request.GET.get("bet_id", None)
        odds_id = self.request.GET.get("odds", None)
        bookie_id = None
        bookie_name = ""
        items = None
        bet_amt = 0
        win_amt = 0
        if action_type in("update","settle",):
            bet = get_object_or_404(Bet, id=bet_id)
            bet_amt = bet.bet_amt
            bet_status = bet.status
            win_amt = bet.win_amt
            if bet_status == Bet.SETTLED:
                win_amt = bet.bet_amt * bet.result_value
            items = BetOdd.objects.filter(bet_id=bet_id).annotate(odd_name=F("odd__bet_type__name"),
                                                                   odd_param=F("odd__param"),
                                                                   odd_team=F("odd__team"),
                                                                   odd_period=F("odd__period"),
                                                                   odd_yes=F("odd__yes"),
                                                                   bookie_name=F("odd__bookie__name"),
                                                                   h_name=F("match__team_h__name"),
                                                                   a_name=F("match__team_a__name"),
                                                                   league_name=F("match__league__name"),
                                                                   ).values()
            bookie_id = bet.bookie_id
            bookie_name = bet.bookie.name
        else:
            action_type = "create"
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

        context["action_type"] = action_type
        context["odds_id"] = odds_id
        context["bet_id"] = bet_id
        context["items"] = items
        context["bookie_id"] = bookie_id
        context["bookie_name"] = bookie_name
        context["bet_amt"] = bet_amt
        context["win_amt"] = win_amt
        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                bookie_id = int(self.request.POST.get('bookie_id'))
                bet_amt_str = self.request.POST.get('bet_amt')
                bet_amt = None if bet_amt_str == None or bet_amt_str == "None" else Decimal(bet_amt_str)
                ids = self.request.POST.getlist('id')
                action_type = self.request.POST.get('action_type')
                bet_id = self.request.POST.get('bet_id')
                bet = None
                if bet_id and bet_id != "None":
                    bet = get_object_or_404(Bet, id=bet_id)
                items = [{
                            "id": None if id == None else int(id),
                            "odd_id":int(self.request.POST['odd_id-{}'.format(id)]),
                            "odd_name":self.request.POST['odd_name-{}'.format(id)],
                            "odd_value":Decimal(self.request.POST['odd_value-{}'.format(id)]),
                            "predictor_id":int(self.request.POST['predictor_id-{}'.format(id)]),
                            "result_value":None if self.request.POST['result_value-{}'.format(id)] == "None" else Decimal(self.request.POST['result_value-{}'.format(id)]),
                            "match_id":int(self.request.POST['match_id-{}'.format(id)]),
                            "harvest_id":int(self.request.POST['harvest_id-{}'.format(id)]),
                            "success_chance":Decimal(self.request.POST['success_chance-{}'.format(id)]),
                            "lose_chance":Decimal(self.request.POST['lose_chance-{}'.format(id)]),
                          }for id in ids]
                if action_type == "create":
                    bet = Bet.api_create(bookie_id, items, bet_amt)
                elif action_type == "update":
                    bet.api_update_odds(items, bet_amt)
                elif action_type == "settle":
                    finished = (self.request.POST.get("finished","0") == "1")
                    win_amt = Decimal(self.request.POST.get('win_amt'))
                    bet.api_settle_odds(items, finished, win_amt)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Creating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



class BetOddAPI(ListAPIView):
    serializer_class = BetOddSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pk",0)
        queryset = BetOdd.objects.filter(bet_id=id).annotate(match_name = Concat(F('match__team_h__name'), V(' - '), F('match__team_a__name')))
        return queryset


class MyBetDelete(BSModalUpdateView):
    model = Bet
    template_name = 'betting/my_bet_detail.html'
    form_class = BetForm
    success_message = "Success: Bet was deleted."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(MyBetDelete, self).get_context_data(**kwargs)
        context["delete_action"] = 1
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                self.object.api_delete()
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  Transaction
####################################################
class TransactionView(generic.TemplateView):
    template_name = "betting/transaction_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TransactionView, self).get_context_data(**kwargs)
        context["bookies"] = LoadSource.objects.filter(is_betting=True).order_by("pk")

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if not date_from:
            date_from = (date.today() - timedelta(1)).strftime('%d.%m.%Y')
        context["date_from"] = date_from
        selected_bookie = self.request.GET.get("bookie", None)
        if selected_bookie:
            context["selected_bookie"] = int(selected_bookie)

        return context    


class TransactionAPI(ListAPIView):
    serializer_class = TransactionSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = Transaction.objects.all()

        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(trans_date__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(trans_date__lte=date_to)
        bookie = self.request.query_params.get("selected_bookie", None)
        if bookie and int(bookie) > 0:
            queryset = queryset.filter(bookie=bookie)

        return queryset


class TransactionCreateView(BSModalCreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'betting/create_transaction.html'
    success_message = "Success: Transaction was created."

    def get_success_message(self):
        return self.success_message
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_initial(self):
        trans_date = date.today()
        return {'trans_date':trans_date,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TransactionCreateView, self).get_context_data(**kwargs)
        context["bookies"] = LoadSource.objects.filter(is_betting=True).order_by("pk")
        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                bookie = cleaned_data["bookie"]
                trans_type = cleaned_data["trans_type"]
                amount = cleaned_data["amount"]
                comment = cleaned_data["comment"]
                trans_date = cleaned_data["trans_date"]

                Transaction.api_add(bookie_id=bookie.id, trans_type=trans_type, amount=amount, comment=comment, trans_date=trans_date)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Creating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class TransactionDeleteView(BSModalUpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'betting/delete_transaction.html'
    success_message = "Success: Transaction was deleted."

    def get_success_message(self):
        return self.success_message
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                self.object.api_delete()
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())
