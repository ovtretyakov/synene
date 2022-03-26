import traceback
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging

from django.db import models, transaction
from django.utils import timezone
from django.db.models import sql, F, Q, Count, Max

from .betting import ValueType, Odd
from .forecast import ForecastSet, Predictor, Harvest
from project.core.models import Sport, Match, League, Country, Team, LoadSource
from project.load.models import ErrorLog


logger = logging.getLogger(__name__)


###################################################################
class SelectedOdd(models.Model):

    forecast_set = models.ForeignKey(ForecastSet, on_delete=models.CASCADE, verbose_name='Forecast set')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE, verbose_name='Odd')
    predictor = models.ForeignKey(Predictor, on_delete=models.CASCADE, verbose_name='Predictor')
    match_date = models.DateField('Match date', null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    kelly = models.DecimalField('Kelly', max_digits=10, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["forecast_set", "odd", ], name='unique_selected_odd'),
        ]

    def __str__(self):
        return f'Set:{self.forecast_set},M:<{self.match},{self.match_date}>,Odd:<{self.odd}>,P:{self.predictor},R:{round(self.result_value,4)},S:{round(self.success_chance,4)}'

    @classmethod
    def api_add(cls, items):
        try:
            with transaction.atomic():
                cls.add(items)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Selecting odd Error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    @classmethod
    def api_delete_odd(cls, odd_id):
        try:
            with transaction.atomic():
                n = 0
                for obj in cls.objects.filter(odd_id=odd_id):
                    n += 1
                    obj.delete_object()
                return n
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Unselect odd error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    @classmethod
    def api_delete_by_idds(cls, ids, obj_type=0):
        try:
            with transaction.atomic():
                queryset = None
                if obj_type == 0:
                    queryset = SelectedOdd.objects.filter(id__in=ids)
                elif obj_type == 1:
                    queryset = SelectedOdd.objects.filter(match_id__in=ids)
                elif obj_type == 2:
                    queryset = SelectedOdd.objects.filter(match__league_id__in=ids)

                n = 0
                for select_odd in queryset:
                    select_odd.delete_object()
                    n += 1
                return n
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Delete selected odds error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    @classmethod
    def api_delete_all(cls):
        try:
            with transaction.atomic():
                n = 0
                for obj in cls.objects.all():
                    obj.delete_object()
                    n += 1
                return n
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Delete all selected odds Error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    def api_delete(self):
        try:
            with transaction.atomic():
                self.delete_object()
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Delete selected odd Error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    @classmethod
    def add(cls, items):
        i = 0
        for item in items:
            i += 1
            forecast_set_id = item.get("forecast_set_id")
            predictor_id = item.get("predictor_id")
            odd_id = item.get("odd_id")
            if not forecast_set_id:
                raise ValueError(f'Missing parameter "forecast_set" for odd {{i}}')
            if not predictor_id:
                raise ValueError(f'Missing parameter "predictor" for odd {{i}}')
            if not odd_id:
                raise ValueError(f'Missing parameter "odd" for odd {{i}}')

            old_selected_odd = SelectedOdd.objects.filter(forecast_set_id=forecast_set_id, odd_id=odd_id).first()
            if old_selected_odd:
                predictor = Predictor.objects.get(pk=predictor_id)
                old_predictor = old_selected_odd.predictor
                if old_predictor.priority < predictor.priority:
                    continue
                old_selected_odd.delete()
            SelectedOdd.objects.create( forecast_set_id = forecast_set_id,
                                        match_id = item.get("match_id"),
                                        odd_id = odd_id,
                                        predictor_id = predictor_id,
                                        match_date = item.get("match_date"),
                                        harvest_id = item.get("harvest_id"),
                                        success_chance = item.get("success_chance"),
                                        lose_chance = item.get("lose_chance"),
                                        result_value = item.get("result_value"),
                                        kelly = item.get("kelly")
                                        )
            Odd.update_selected(odd_id)


    def delete_object(self):
        odd_id = self.odd_id
        self.delete()
        Odd.update_selected(odd_id)


###################################################################
class Saldo(models.Model):
    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Bookie')
    saldo_date = models.DateField('Saldo date')
    saldo_amt  = models.DecimalField('Saldo', max_digits=10, decimal_places=2)
    in_amt  = models.DecimalField('In', max_digits=10, decimal_places=2)
    out_amt  = models.DecimalField('Out', max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["bookie", "saldo_date", ], name='unique_saldo'),
        ]

    def __str__(self):
        return f'{self.bookie}:{self.saldo_date}:{self.saldo_amt}'


    @classmethod
    def add_transaction(cls, bookie_id, trans_date, trans_amt):
        in_amt = trans_amt if trans_amt > 0 else 0
        out_amt = -1*trans_amt if trans_amt < 0 else 0
        cls._update_saldo(bookie_id, trans_date, trans_amt, in_amt, out_amt)

    @classmethod
    def del_transaction(cls, bookie_id, trans_date, trans_amt):
        in_amt = -1*trans_amt if trans_amt > 0 else 0
        out_amt = trans_amt if trans_amt < 0 else 0
        cls._update_saldo(bookie_id, trans_date, -1*trans_amt, in_amt, out_amt)

    @classmethod
    def _update_saldo(cls, bookie_id, saldo_date, amount, in_amt, out_amt):
        saldo = Saldo.objects.filter(bookie_id=bookie_id, saldo_date__lte=saldo_date).order_by("-saldo_date").first()
        if not saldo:
            saldo = Saldo(
                            bookie_id=bookie_id,
                            saldo_date=saldo_date,
                            saldo_amt=0,
                            in_amt=0,
                            out_amt=0,
                         )
        if saldo.saldo_date != saldo_date:
            saldo.saldo_date = saldo_date
            saldo.id = None
            saldo.in_amt = 0
            saldo.out_amt = 0
        saldo.saldo_amt += amount
        saldo.in_amt += in_amt
        saldo.out_amt += out_amt
        saldo.save()

        Saldo.objects.filter(bookie_id=bookie_id, saldo_date__gt=saldo_date).update(saldo_amt=F("saldo_amt")+amount)
        current_saldo = Saldo.objects.filter(bookie_id=bookie_id).order_by("-saldo_date").first()
        LoadSource.objects.filter(pk=bookie_id).update(saldo_amt=current_saldo.saldo_amt)


###################################################################
class Transaction(models.Model):

    #Type
    TYPE_IN       = 'i'
    TYPE_OUT      = 'o'
    TYPE_CORRECT  = 'c'
    TYPE_BID      = 'b'
    TYPE_WIN      = 'w'

    TYPE_CHOICES = (
        (TYPE_IN, 'In'),
        (TYPE_OUT, 'Out'),
        (TYPE_CORRECT, 'Correct`'),
        (TYPE_BID, 'Bid'),
        (TYPE_WIN, 'Win'),
    )

    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Bookie')
    trans_type = models.CharField('Type', max_length=5, choices=TYPE_CHOICES)
    trans_date = models.DateField('Transaction date')
    ins_time = models.DateTimeField('Ins time')
    amount  = models.DecimalField('Amount', max_digits=10, decimal_places=2)
    comment = models.CharField('Comment', max_length=2000, blank=True)

    def __str__(self):
        return f'{self.id}:{self.bookie}:{self.trans_type}:{self.trans_date}:{self.amount}'

    class Meta:
        indexes = [
            models.Index(fields=['trans_date',], name='transaction_date_idx'),
        ]


    @classmethod
    def api_add(cls, bookie_id, trans_type, amount, comment="", trans_date=date.today()):
        try:
            with transaction.atomic():
                return cls.add(bookie_id, trans_type, amount, comment, trans_date)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Create transaction error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e

    def api_delete(self):
        try:
            with transaction.atomic():
                self.delete_object()
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Delete transaction error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e



    @classmethod
    def add(cls, bookie_id, trans_type, amount, comment="", trans_date=date.today()):
        transaction = Transaction.objects.create(
                                                bookie_id=bookie_id,
                                                trans_type=trans_type,
                                                trans_date=trans_date,
                                                ins_time=datetime.now(),
                                                amount=amount,
                                                comment=comment
                                               )
        Saldo.add_transaction(bookie_id, trans_date, amount)
        return transaction

    def delete_object(self):
        bookie_id = self.bookie_id
        trans_date = self.trans_date
        amount = self.amount
        self.delete()
        Saldo.del_transaction(bookie_id, trans_date, amount)

###################################################################
class Bet(models.Model):

    #Status
    SETTLED  = 's'
    UNSETTLED = 'u'
    BID = 'b'
    FINISHED = 'f'

    #Result
    UNKNOWN       = 'n'
    SUCCESS       = 's'
    PART_SUCCESS  = 'sp'
    RETURN        = 'r'
    PART_FAIL     = 'fp'
    FAIL          = 'f'

    #betting_type
    SINGLE  = 's'
    EXPRESS = 'e'

    STATUS_CHOICES = (
        (SETTLED, 'Settled'),
        (UNSETTLED, 'Unsettled'),
        (BID, 'Bid'),
        (FINISHED, 'Finished'),
    )
    RESULT_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (SUCCESS, 'Success'),
        (PART_SUCCESS, 'Part success'),
        (RETURN, 'Return'),
        (PART_FAIL, 'Part fail'),
        (FAIL, 'Fail'),
    )
    BETTING_TYPE_CHOICES = (
        (SINGLE, 'Single'),
        (EXPRESS, 'Express'),
    )

    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Bookie', null=True)
    name = models.CharField("Bet name", max_length=255, blank=True)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='u')
    result = models.CharField('Result', max_length=5, choices=RESULT_CHOICES)
    betting_type = models.CharField('Betting type', max_length=5, choices=BETTING_TYPE_CHOICES)
    odd_cnt = models.IntegerField('Odd cnt', default=0)
    ins_time = models.DateTimeField('Ins time')
    bid_time = models.DateTimeField('Bid time', null=True)
    settled_time = models.DateTimeField('Settled time', null=True)
    finish_time = models.DateTimeField('Finish time', null=True)
    min_date = models.DateField('Min odd date', null=True)
    max_date = models.DateField('Max odd date', null=True)
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3, null=True)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3, null=True)
    odd_value = models.DecimalField('Odd value', max_digits=10, decimal_places=3, null=True)
    expect_value = models.DecimalField('Expect value', max_digits=10, decimal_places=3, null=True)
    kelly = models.DecimalField('Kelly', max_digits=10, decimal_places=3, null=True)
    bet_amt = models.DecimalField('Bet amt', max_digits=10, decimal_places=2, null=True)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3, null=True)
    win_amt = models.DecimalField('Win amt', max_digits=10, decimal_places=2, null=True)
    bet_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, verbose_name='Bet trans', null=True,
                                        related_name='betting_bet_bet_trans_fk')
    win_transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, verbose_name='Win trans', null=True,
                                        related_name='betting_bet_win_trans_fk')

    def __str__(self):
        return f'{self.id}:{self.bookie}:{self.name}:{self.betting_type}:{self.status}:{self.result}:{self.bet_amt}:{self.win_amt}'

    class Meta:
        indexes = [
            models.Index(fields=['ins_time',], name='bet_ins_time_idx'),
        ]


    @classmethod
    def api_create(cls, bookie_id, items, bet_amt=0):
        try:
            with transaction.atomic():
                return cls.create(bookie_id, items, bet_amt)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Create bet error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e

    def api_update_odds(self, items, bet_amt=0):
        try:
            with transaction.atomic():
                return self.update_odds(items, bet_amt)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Update bet error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    def api_delete_odds(self, items):
        try:
            with transaction.atomic():
                return self.delete_odds(items)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Delete bet error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e


    @classmethod
    def create(cls, bookie_id, items, bet_amt=0):
        betting_type = Bet.SINGLE if len(items) <= 1 else Bet.EXPRESS
        status = Bet.BID if bet_amt and bet_amt > 0 else Bet.UNSETTLED
        bet = Bet.objects.create(
                                bookie_id=bookie_id,
                                name="",
                                status=Bet.UNSETTLED,
                                result=Bet.UNKNOWN,
                                betting_type=betting_type,
                                ins_time=timezone.now(),
                                bet_amt=0,
                                win_amt=0
                                )
        BetOdd.add(bet, items)
        if status == Bet.BID:
            bet._do_bet(bet_amt)

        return bet

    def update_odds(self, items, bet_amt=0):
        status = Bet.BID if bet_amt and bet_amt > 0 else Bet.UNSETTLED
        BetOdd.update_odds(self, items)
        if status == Bet.BID:
            self._do_bet(bet_amt)

    def delete_odds(self, items):
        BetOdd.delete_odds(self, items)

    def delete_object(self):
        items = BetOdd.objects.filter(bet_id=self.id).values()
        BetOdd.delete_odds(self, items, force=True)
        if self.win_transaction:
            self.win_transaction.delete_object()
        if self.bet_transaction:
            self.bet_transaction.delete_object()
        self.delete()

    def settle_odds(self, items, finished=False, win_amt=0):
        if finished and (self.status == Bet.UNSETTLED or self.status == Bet.FINISHED):
            raise ValueError(f'Incorrect bet status "{self.status}"')
        BetOdd.settle_odds(self, items, finished)
        if finished:
            self._do_finish(win_amt)

    def _do_bet(self, bet_amt):
        bet_transaction = Transaction.add(bookie_id=self.bookie_id, trans_type=Transaction.TYPE_BID, amount=-1*bet_amt)
        self.status = Bet.BID
        self.bid_time = timezone.now()
        self.bet_amt = bet_amt
        self.bet_transaction = bet_transaction
        self.save()

    def _do_finish(self, win_amt):
        win_transaction = Transaction.add(bookie_id=self.bookie_id, trans_type=Transaction.TYPE_WIN, amount=win_amt)
        self.status = Bet.FINISHED
        self.win_time = timezone.now()
        self.win_amt = win_amt
        self.win_transaction = win_transaction
        self.save()

    def _update(self):
        name = ""
        betting_type = Bet.SINGLE
        min_date = None    
        max_date = None    
        success_chance  = 0
        lose_chance  = 0
        odd_value = None
        expect_value = None
        kelly = 0
        result_value = None
        odd_cnt = 0
        all_settled = True
        for bet_odd in BetOdd.objects.filter(bet_id=self.id).order_by("pk"):
            odd_cnt += 1
            if not name:
                name = bet_odd.match.team_h.name + " - " + bet_odd.match.team_a.name
            if not min_date or min_date > bet_odd.match_date:
                min_date = bet_odd.match_date
            if not max_date or max_date < bet_odd.match_date:
                max_date = bet_odd.match_date
            if not success_chance:
                success_chance = bet_odd.success_chance
            else:
                success_chance = success_chance * bet_odd.success_chance
            if not odd_value:
                odd_value = bet_odd.odd_value
            else:
                odd_value = odd_value * bet_odd.odd_value
            if not expect_value:
                expect_value = bet_odd.expect_value
            else:
                expect_value = expect_value * bet_odd.expect_value
            if bet_odd.result_value != None:
                if result_value == None:
                    result_value = bet_odd.result_value
                else:
                    result_value = result_value * bet_odd.result_value
            if bet_odd.status == BetOdd.UNSETTLED:
                all_settled = False

        if odd_cnt > 1:
            betting_type = Bet.EXPRESS
        if not name:
            name = f"Bet {self.pk}"
        if success_chance:
            lose_chance = Decimal("1.0") - success_chance
        if expect_value and expect_value > 1.001:
            kelly = (expect_value - Decimal(1.0)) / (odd_value - Decimal(1.0))

        self.name = name
        self.betting_type = betting_type
        self.min_date = min_date
        self.max_date = max_date  
        self.success_chance = success_chance
        self.lose_chance = lose_chance
        self.odd_value = odd_value
        self.expect_value = expect_value
        self.kelly = kelly
        self.result_value = result_value
        self.odd_cnt = odd_cnt
        if all_settled and self.status == Bet.BID:
            if result_value == None:
                result = Bet.UNKNOWN
            elif result_value <= 0:
                result = Bet.FAIL
            elif result_value < 1:
                result = Bet.PART_FAIL
            elif result_value == 1:
                result = Bet.RETURN
            elif result_value < bet_odd.odd_value:
                result = Bet.PART_SUCCESS
            else:
                result = Bet.SUCCESS
            self.result = result
            self.status = Bet.SETTLED
            self.settled_time = timezone.now()
        self.save()

###################################################################
class BetOdd(models.Model):

    #Status
    SETTLED  = 's'
    UNSETTLED = 'u'
    FINISHED = 'f'

    #Result
    UNKNOWN       = 'n'
    SUCCESS       = 's'
    PART_SUCCESS  = 'sp'
    RETURN        = 'r'
    PART_FAIL     = 'fp'
    FAIL          = 'f'

    STATUS_CHOICES = (
        (SETTLED, 'Settled'),
        (UNSETTLED, 'Unsettled'),
        (FINISHED, 'Finished'),
    )
    RESULT_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (SUCCESS, 'Success'),
        (PART_SUCCESS, 'Part success'),
        (RETURN, 'Return'),
        (PART_FAIL, 'Part fail'),
        (FAIL, 'Fail'),
    )

    bet = models.ForeignKey(Bet, on_delete=models.CASCADE, verbose_name='Bet', null=True)
    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Bookie', null=True)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='u')
    result = models.CharField('Result', max_length=5, choices=RESULT_CHOICES)
    ins_time = models.DateTimeField('Ins time')
    settled_time = models.DateTimeField('Settled time', null=True)
    finish_time = models.DateTimeField('Finish time', null=True)
    match = models.ForeignKey(Match, on_delete=models.SET_NULL, verbose_name='Match', null=True)
    odd = models.ForeignKey(Odd, on_delete=models.SET_NULL, verbose_name='Odd', null=True)
    predictor = models.ForeignKey(Predictor, on_delete=models.SET_NULL, verbose_name='Predictor', null=True)
    match_date = models.DateField('Match date', null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.SET_NULL, verbose_name='Harvest', null=True)
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3, null=True)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3, null=True)
    odd_value = models.DecimalField('Odd value', max_digits=10, decimal_places=3, null=True)
    expect_value = models.DecimalField('Expect value', max_digits=10, decimal_places=3, null=True)
    kelly = models.DecimalField('Kelly', max_digits=10, decimal_places=3, null=True)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3, null=True)

    def __str__(self):
        return f'{self.id}:{self.bookie}:{self.match_id}:{self.status}:{self.result}:{self.odd_value}:{self.expect_value}:{self.result_value}'

    class Meta:
        indexes = [
            models.Index(fields=['match_date',], name='betodd_match_date_idx'),
            models.Index(fields=['ins_time',], name='betodd_ins_time_idx'),
        ]

    @classmethod
    def add(cls, bet, items):
        if bet.status != Bet.UNSETTLED:
            raise ValueError(f'Incorrect bet status "{bet.status}"')

        for item in items:
            odd = Odd.objects.get(pk=item.get("odd_id"))
            predictor_id=item.get("predictor_id")
            odd_value = item.get("odd_value")
            if not odd_value:
                raise ValueError(f'Empty odd_value for odd "{odd}"')
            if odd_value != odd.odd_value and predictor_id:
                predictor = Predictor.objects.get(pk=predictor_id)
                odd.odd_value = odd_value
                success_chance, lose_chance, result_value, kelly = predictor.forecasting_odd(odd)
            else:
                result_value = item.get("result_value")
                kelly = 0
                if result_value > 1.001:
                    kelly = (result_value - Decimal(1.0)) / (odd_value - Decimal(1.0))

            BetOdd.objects.create(
                                    bet_id=bet.id,
                                    bookie_id=bet.bookie_id,
                                    status=BetOdd.UNSETTLED,
                                    result=BetOdd.UNKNOWN,
                                    ins_time=timezone.now(),
                                    match_id=item.get("match_id"),
                                    odd_id=item.get("odd_id"),
                                    predictor_id=item.get("predictor_id"),
                                    match_date=item.get("match_date"),
                                    harvest_id=item.get("harvest_id"),
                                    success_chance=item.get("success_chance"),
                                    lose_chance=item.get("lose_chance"),
                                    odd_value=odd_value,
                                    expect_value = result_value,
                                    kelly = kelly,
                                )

            Odd.update_selected(odd.id)
        bet._update()


    @classmethod
    def update_odds(cls, bet, items):
        if bet.status != Bet.UNSETTLED:
            raise ValueError(f'Incorrect bet status "{bet.status}"')

        i = 0
        for item in items:
            i += 1
            id = item.get("id")
            if not id:
                raise ValueError(f'Empty id for row "{i}"')

            bet_odd = BetOdd.objects.get(id=id, bet_id=bet.id)
            odd_id = bet_odd.odd_id
            is_del = item.get("is_del",0)
            if is_del:
                bet_odd.delete()
            else:
                odd_value = item.get("odd_value")
                if odd_value != bet_odd.odd_value:
                    if bet_odd.predictor_id:
                        predictor = bet_odd.predictor
                        predictor = bet_odd.predictor.get_real_predictor()
                        odd = Odd.objects.get(pk=odd_id)
                        odd.odd_value = odd_value
                        success_chance, lose_chance, expect_value, kelly = predictor.forecasting_odd(odd)
                        bet_odd.odd_value = odd_value
                        bet_odd.expect_value = expect_value
                        bet_odd.kelly = kelly
                        bet_odd.save()
            Odd.update_selected(odd_id)
        bet._update()        


    @classmethod
    def delete_odds(cls, bet, items, force=False):
        if not force and bet.status != Bet.UNSETTLED:
            raise ValueError(f'Incorrect bet status "{bet.status}"')

        i = 0
        for item in items:
            i += 1
            id = item.get("id")
            if not id:
                raise ValueError(f'Empty id for row "{i}"')

            bet_odd = BetOdd.objects.get(id=id, bet_id=bet.id)
            odd_id = bet_odd.odd_id
            bet_odd.delete()
            Odd.update_selected(odd_id)
        bet._update()                


    @classmethod
    def settle_odds(cls, bet, items, finished=False):
        if bet.status == Bet.FINISHED:
            raise ValueError(f'Incorrect bet status "{bet.status}"')

        i = 0
        for item in items:
            i += 1
            id = pk=item.get("id")
            if not id:
                raise ValueError(f'Empty id for row "{i}"')

            bet_odd = BetOdd.objects.get(id=id, bet_id=bet.id)
            if not finished and bet_odd.status != BetOdd.UNSETTLED or finished and bet_odd.status == BetOdd.FINISHED:
                continue
            result_value = item.get("result_value")
            if bet_odd.status == BetOdd.UNSETTLED:
                if result_value == None:
                    raise ValueError(f'No result_value for odd "{bet_odd.odd}"')
                if result_value <= 0:
                    result = BetOdd.FAIL
                elif result_value < 1:
                    result = BetOdd.PART_FAIL
                elif result_value == 1:
                    result = BetOdd.RETURN
                elif result_value < bet_odd.odd_value:
                    result = BetOdd.PART_SUCCESS
                else:
                    result = BetOdd.SUCCESS
                bet_odd.result_value = result_value
                bet_odd.result = result
            bet_odd.status = BetOdd.FINISHED if finished else BetOdd.SETTLED
            if not bet_odd.settled_time:
                bet_odd.settled_time = timezone.now()
            if finished:
                bet_odd.settled_time = timezone.now()
            bet_odd.save()
        if finished:
            BetOdd.objects.filter(bet_id=bet.id, status=BetOdd.SETTLED).update(status=BetOdd.FINISHED, finish_time = timezone.now())
            bet_odd = BetOdd.objects.filter(bet_id=bet.id).exclude(status=BetOdd.FINISHED).order_by("id").first()
            if bet_odd:
                raise ValueError(f'Not finished odd "{bet_odd.odd}"')
        bet._update()        

    @classmethod
    def settle_by_odd(cls, odd):
        for bet_odd in BetOdd.objects.filter(odd_id=odd.id, status=BetOdd.UNSETTLED):
            bet = Bet.objects.get(pk=bet_odd.bet_id)
            bet_odd.status = BetOdd.SETTLED
            bet_odd.result_value = odd.result_value
            bet_odd.result = odd.result
            bet_odd.settled_time = timezone.now()
            bet_odd.save()
            bet._update()        
