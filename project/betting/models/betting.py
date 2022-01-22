import traceback
from decimal import Decimal
import logging

from django.db import models
from django.utils import timezone

from project.core.models import Mergable, LoadSource, Match, League, Country, Team
from .. import mixins as OddMixins
from project.core.utils import (get_int, list_get,
                        get_match_result, 
                        get_total_over_result, get_total_under_result, 
                        get_handicap_result)

logger = logging.getLogger(__name__)

###################################################################
class ValueType(models.Model):
    '''Describe what is the value for which the rate applies
       Ex: goals, corners, yellow cards, etc.
    '''

    MAIN            = 'main'
    CORNER          = 'corner'
    Y_CARD          = 'ycard'
    R_CARD          = 'rcard'
    FOUL            = 'foul'
    SHOT_ON_GOAL    = 'shot-on-goal'
    SHOT            = 'shot'
    OFFSIDE         = 'offside'
    POSSESSION      = 'ball-possession'
    PENALTY         = 'penalty'

    STAT_TYPE_MAPPING = {
        MAIN:Match.GOALS,
        CORNER:Match.CORNERS,
        Y_CARD:Match.YCARD,
        R_CARD:Match.RCARD,
        FOUL:Match.FOULS,
        SHOT_ON_GOAL:Match.SHOTS_ON_TARGET,
        SHOT:Match.SHOTS,
        OFFSIDE:Match.OFFSIDES,
        POSSESSION:Match.POSSESSION,
        PENALTY:Match.PENALTY,
    }

    slug = models.SlugField(unique=True)
    name = models.CharField('Type', max_length=100)

    def __str__(self):
        return self.name

    @staticmethod
    def get(slug):
        return ValueType.objects.get(slug=slug)

    def get_stat_type(self):
        '''Return correcponding MatchStat.stat_type'''
        return ValueType.STAT_TYPE_MAPPING.get(self.slug,None)


###################################################################
class BetType(models.Model):

    WDL                               = 'wdl'
    WDL_MINUTE                        = 'wdl_minute'
    RESULT_HALF1_FULL                 = 'result_half1_full'
    RESULT_HALF1_HALF2                = 'result_half1_half2'
    WIN_BOTH                          = 'win_both'
    WIN_LEAST_ONE_HALF                = 'win_least_one_half'
    WIN_TO_NIL                        = 'win_to_nil'
    CORRECT_SCORE                     = 'correct_score'
    TOTAL_EVEN_ODD                    = 'total_even_odd'
    TOTAL_OVER                        = 'total_over'
    TOTAL_UNDER                       = 'total_under'
    TOTAL_BOTH_HALVES_OVER            = 'total_both_halves_over'
    TOTAL_BOTH_HALVES_UNDER           = 'total_both_halves_under'
    TOTAL_OVER_MINUTES                = 'total_over_minutes'
    TOTAL_UNDER_MINUTES               = 'total_under_minutes'
    TOTAL                             = 'total'
    HANDICAP                          = 'handicap'
    HANDICAP_MINUTES                  = 'handicap_minutes'
    CONSECUTIVE_GOALS                 = 'consecutive_goals'
    ITOTAL_BOTH_OVER                  = 'itotal_both_over'
    ITOTAL_BOTH_UNDER                 = 'itotal_both_under'
    ITOTAL_ONLY_OVER                  = 'itotal_only_over'
    ITOTAL_ONLY_UNDER                 = 'itotal_only_under'
    ITOTAL_AT_LEAST_OVER              = 'itotal_at_least_over'
    ITOTAL_AT_LEAST_UNDER             = 'itotal_at_least_under'
    MARGIN                            = 'margin'
    W_AND_TOTAL_OVER                  = 'w_and_total_over'
    W_AND_TOTAL_UNDER                 = 'w_and_total_under'
    WD_AND_TOTAL_OVER                 = 'wd_and_total_over'
    WD_AND_TOTAL_UNDER                = 'wd_and_total_under'
    BOTH_TO_SCORE_AND_TOTAL_OVER      = 'both_to_score_and_total_over'
    BOTH_TO_SCORE_AND_TOTAL_UNDER     = 'both_to_score_and_total_under'
    NOT_BOTH_TO_SCORE_AND_TOTAL_OVER  = 'not_both_to_score_and_total_over'
    NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER = 'not_both_to_score_and_total_under'
    WDL_AND_BOTH_TEAMS_SCORE          = 'wdl_and_both_teams_score'
    BOTH_TO_SCORE_AT_1_2              = 'both_to_score_at_1_2'
    ITOTAL_BOTH_OVER_IN_BOTH_HALVES   = 'itotal_both_over_in_both_halves'
    ITOTAL_BOTH_UNDER_IN_BOTH_HALVES  = 'itotal_both_under_in_both_halves'
    ITOTAL_ONLY_OVER_IN_BOTH_HALVES   = 'itotal_only_over_in_both_halves'
    ITOTAL_ONLY_UNDER_IN_BOTH_HALVES  = 'itotal_only_under_in_both_halves'
    ITOTAL_BOTH_OVER_AND_EITHER_WIN   = 'itotal_both_over_and_either_win'
    RACE_TO_GOALS                     = 'race_to_goals'
    HALF_TO_SCORE_FIRST_GOAL          = 'half_to_score_first_goal'
    TIME_TO_SCORE_FIRST_GOAL          = 'time_to_score_first_goal'
    DRAW_IN_EITHER_HALF               = 'draw_in_either_half'
    HIGHEST_VALUE_HALF                = 'highest_value_half'
    WIN_NO_BET                        = 'win_no_bet'
    # DRAW_LEAST_ONE_HALF               = 'draw_least_one_half'
    W_AND_ITOTAL_OVER                 = 'w_and_itotal_over'
    W_AND_ITOTAL_UNDER                = 'w_and_itotal_under'
    WD_AND_ITOTAL_OVER                = 'wd_and_itotal_over'
    WD_AND_ITOTAL_UNDER               = 'wd_and_itotal_under'
    W_AND_TOTAL                       = 'w_and_total'
    # PENALTY_AND_R_CARD                = 'penalty_and_r_card'
    # PENALTY_OR_R_CARD                 = 'penalty_or_r_card'
    # Y_AND_R_CARDS_OVER                = 'y_and_r_cards_over'
    # Y_AND_R_CARDS_UNDER               = 'y_and_r_cards_under'


    slug = models.SlugField(unique=True)
    name = models.CharField('Type', max_length=100)
    description = models.CharField('Description', max_length=2000, null=True, blank=True)
    handler = models.CharField('Handler', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get(slug):
        return BetType.objects.get(slug=slug)

###################################################################
class OddBookieConfig(models.Model):

    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Bookie')
    code = models.CharField('Odd code', max_length=100)
    name = models.CharField('Odd name', max_length=255, null=True, blank=True)
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, verbose_name='Bet type', null=True)
    period = models.IntegerField('Period', null=True, blank=True)
    param = models.CharField('Param', max_length=255, blank=True)
    team = models.CharField('Team', max_length=10, blank=True)
    yes = models.CharField(r'Yes\No', max_length=1)
    bookie_handler = models.CharField('Handler', max_length=100, blank=True)
    value_type = models.CharField('Value Type', max_length=20, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bookie','code'], name='unique_odd_bookie_conf'),
        ]

    def __str__(self):
        return self.name



###################################################################
class Odd(Mergable, models.Model):

    #Status
    WAITING  = 'w'
    FINISHED = 'f'
    CANCELLED = 'c'

    #Result
    UNKNOWN       = 'n'
    SUCCESS       = 's'
    PART_SUCCESS  = 'sp'
    RETURN        = 'r'
    PART_FAIL     = 'fp'
    FAIL          = 'f'

    YES_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    TEAM_CHOICES = (
        ('h', 'Home'),
        ('a', 'Away'),
    )
    STATUS_CHOICES = (
        (WAITING, 'Waiting'),
        (FINISHED, 'Finished'),
        (CANCELLED, 'Cancelled'),
    )
    RESULT_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (SUCCESS, 'Success'),
        (PART_SUCCESS, 'Part success'),
        (RETURN, 'Return'),
        (PART_FAIL, 'Part fail'),
        (FAIL, 'Fail'),
    )


    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    bet_type = models.ForeignKey(BetType, on_delete=models.PROTECT, verbose_name='Bet type')
    bookie = models.ForeignKey(LoadSource, on_delete=models.CASCADE, 
                               verbose_name='Bookie', related_name='betting_odd_bookie_fk')
    odd_bookie_config = models.ForeignKey(OddBookieConfig, on_delete=models.SET_NULL, null=True, verbose_name='Bookie Odd')
    value_type = models.ForeignKey(ValueType, on_delete=models.PROTECT, verbose_name='Value type')
    period = models.IntegerField('Period')
    yes = models.CharField(r'Yes\No', max_length=1, choices=YES_CHOICES)
    team = models.CharField('Team', max_length=10, blank=True, choices=TEAM_CHOICES)
    param = models.CharField('Param', max_length=255, blank=True)
    odd_value = models.DecimalField('Odd', max_digits=10, decimal_places=3)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES)
    result = models.CharField('Result', max_length=5, choices=RESULT_CHOICES)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True, 
                                    verbose_name='Source', related_name='betting_odd_source_fk')
    odd_update = models.DateTimeField('Odd update', null=True, blank=True)
    result_update = models.DateTimeField('Result update', null=True, blank=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match','bet_type','bookie','value_type','period','yes','team','param'], 
                                    name='unique_odd'),
        ]

    def __str__(self):
        return f'M{self.match},BT{self.bet_type},BO{self.bookie},VT{self.value_type},PE{self.period},Y{self.yes},T{self.team},PA{self.param}'

    @classmethod
    def get_object(cls, match=None,
                    bet_type=None,bet_type_slug=None,
                    value_type=None,value_type_slug=None,
                    bookie=None,period=0,yes="Y",team="",param="", 
                    **kwargs):
        if value_type_slug and not value_type:
            value_type = ValueType.objects.get(slug=value_type_slug) 
        if not value_type:
            value_type = ValueType.objects.get(slug=ValueType.MAIN) 
        if not bookie:
            bookie = LoadSource.objects.get(slug="na")
        if cls.own_bet_type():
            #method is called from real class (not from class Odd)
            bet_type = BetType.objects.get(slug=cls.own_bet_type()) 
            try:
                obj = cls.objects.get(match=match,bet_type=bet_type,bookie=bookie,value_type=value_type,period=period,yes=yes,team=team,param=param)
            except cls.DoesNotExist:
                obj = None
        else:
            #find real class
            if bet_type_slug and not bet_type:
                bet_type = BetType.objects.get(slug=bet_type_slug) 
            real_cls = globals().get(bet_type.handler)
            if not real_cls:
                #cant find real class handler - create default class 
                try:
                    obj = cls.objects.get(match=match,bet_type=bet_type,bookie=bookie,value_type=value_type,period=period,yes=yes,team=team,param=param)
                except cls.DoesNotExist:
                    obj = None
            else:
                try:
                    obj = real_cls.objects.get(match=match,bet_type=bet_type,bookie=bookie,value_type=value_type,period=period,yes=yes,team=team,param=param)
                except real_cls.DoesNotExist:
                    obj = None
        return obj

    @classmethod
    def create(cls, match, bet_type_slug, value_type_slug, load_source, bookie=None, 
                    period=0, yes='Y', team='', param='', odd_value=None, odd_bookie_config=None):
        # match
        if not match: raise ValueError('Missing parameter "match"')
        # bet_type
        if not bet_type_slug:
            logger.error("!!! Missing parameter 'bet_type_slug' match=%s, source=%s, config=%s" %
                         (match, load_source, odd_bookie_config.code)) 
            raise ValueError('Missing parameter "bet_type_slug"')
        try:
            bet_type = BetType.objects.get(slug=bet_type_slug)
        except BetType.DoesNotExist:
            raise ValueError('Unknown bet_type: %s' % bet_type_slug)
        # value_type
        if not value_type_slug: raise ValueError('Missing parameter "value_type_slug"')
        try:
            value_type = ValueType.objects.get(slug=value_type_slug)
        except ValueType.DoesNotExist:
            raise ValueError('Unknown value_type: %s' % value_type_slug)
        # load_source
        if not load_source: raise ValueError('Missing parameter "load_source"')
        # bookie
        if bookie and not bookie.is_betting: raise ValueError('"%s" is not betting source' % bookie)
        if not bookie:
            bookie = LoadSource.objects.get(sport=load_source.sport, slug=LoadSource.SRC_UNKNOWN)

        cls = globals().get(bet_type.handler)
        if not cls: 
            raise ValueError('Unknonwn bet handler "%s"' % bet_type.handler)
            # cls = Odd

        config = ""
        if odd_bookie_config:
            config = odd_bookie_config.code
        period = cls.clean_period(period, match, bet_type_slug, load_source, config)
        yes = cls.clean_yes(yes)
        team = cls.clean_team(team)
        param = cls.clean_param(param)
        odd_value = cls.clean_value(odd_value)

        if odd_value < bookie.min_odd or odd_value > bookie.max_odd:
            #skip odd
            return None

        #if exists
        try:
            if bookie:
                odd = cls.objects.select_related('load_source').get(
                                      match=match,bet_type=bet_type,bookie=bookie,value_type=value_type,
                                      period=period,yes=yes,team=team,param=param)
            else:
                odd = cls.objects.select_related('load_source').get(
                                      match=match,bet_type=bet_type,bookie__isnull=True,value_type=value_type,
                                      period=period,yes=yes,team=team,param=param)
        except Odd.DoesNotExist:
            odd = None

        if odd:
            if load_source.reliability <= odd.load_source.reliability and odd.status == Odd.WAITING:
                changed=False
                if odd_bookie_config and not odd.odd_bookie_config == odd_bookie_config: 
                    odd.odd_bookie_config=odd_bookie_config
                    changed=True
                if odd_value and not odd.odd_value == odd_value: 
                    odd.odd_value=odd_value
                    changed=True
                if changed:
                    odd.load_source=load_source
                    odd.odd_update=timezone.now()
                    odd.save()
        else:

            odd = cls.objects.create(
                                        match=match,
                                        bet_type=bet_type,
                                        bookie=bookie,
                                        odd_bookie_config=odd_bookie_config,
                                        value_type=value_type,
                                        period=period,
                                        yes=yes,
                                        team=team,
                                        param=param,
                                        odd_value=odd_value,
                                        status=Odd.WAITING,
                                        result=Odd.UNKNOWN,
                                        result_value=0,
                                        load_source=load_source,
                                        odd_update=timezone.now()
                                    )
        return odd

    @staticmethod
    def own_bet_type():
        return None

    @classmethod
    def clean_period(cls, period, match="", bet_type="", source="", config=""):
        if not period in(0,1,2,15,30,45,60,75,90,):
            raise ValueError('Invalid period param: %s (match=%s, bet_type=%s, source=%s, config=%s)' % 
                              (period,match,bet_type,source,config))
        return period

    @classmethod
    def clean_yes(cls, yes):
        if yes in('y','n'): yes = yes.upper()
        elif yes.lower() == 'yes': yes = 'Y'
        elif yes == '1': yes = 'Y'
        elif yes.lower() == 'no': yes = 'N'
        elif yes == '0': yes = 'N'
        if not yes in('Y','N',):
            raise ValueError('Invalid yes-no param: %s' % yes)
        return yes

    @classmethod
    def clean_team(cls, team):
        if team in('H','A'): team = team.lower()
        elif team.lower() == 'home': team = 'h'
        elif team.lower() == 'away': team = 'a'
        if not team in('h','a',''):
            raise ValueError('Invalid team param: %s' % team)
        return team

    @classmethod
    def clean_param(cls, param):
        return param

    @classmethod
    def clean_value(cls, value):
        value = round(Decimal(value),5)
        if value < 0:
            raise ValueError('Invalid bet value: %s' % value)
        return value

    def get_own_object(self):
        real_cls = globals().get(self.bet_type.handler)
        if not real_cls:
            obj = self
        else:
            try:
                obj = real_cls.objects.get(pk=self.pk)
            except real_cls.DoesNotExist:
                obj = None
        return obj

    def save(self, *args, **kwargs):
        if self.own_bet_type():
            self.bet_type = self.own_bet_type()
        super(Odd, self).save(*args, **kwargs)

    def change_match(self, match_dst):
        '''Change match'''
        if match_dst == None or match_dst == self.match:
            return
        odd_dst = Odd.get_object(match=match_dst,
                    bet_type=self.bet_type,bookie=self.bookie,value_type=self.value_type,period=self.period,yes=self.yes,team=self.team,param=self.param)
        if odd_dst:
            self.merge_to(odd_dst)
        else:
            self.match = match_dst
            self.save()

    def forecasting(self, forecast_data):
        success_chance = None
        lose_chance = None
        result_value = None
        return success_chance, lose_chance, result_value

    def change_data(self, src):
        self.odd_value = src.odd_value
        self.status = src.status
        self.result = src.result
        self.result_value = src.result_value
        self.odd_update = src.odd_update
        self.result_update = src.result_update
        self.save()
        self.calculate_result()

    def merge_related(self, dst):
        pass

    def get_match_values(self, value_type=None, stat_type=None, period=None):
        if not stat_type:
            if value_type: 
                value_type = ValueType.get(value_type)
            else:
                value_type = self.value_type
            stat_type = value_type.get_stat_type()
        if period == None:
            period = self.period
        return self.match.get_competitors_values(stat_type, period)

    def get_odd_values(self, value_type=None, stat_type=None, period=None):
        '''default method implementation'''
        return self.get_match_values(value_type=value_type, stat_type=stat_type, period=period)

    def get_odd_int_values(self, value_type=None, stat_type=None, period=None, value_h=None, value_a=None):
        if value_h == None or value_h == None:
            value_h, value_a = self.get_odd_values(value_type=value_type, stat_type=stat_type, period=period)
        if value_h: value_h = int(value_h)
        if value_a: value_a = int(value_a)
        return value_h, value_a

    def get_odd_decimal_values(self, value_type=None, stat_type=None, period=None, value_h=None, value_a=None):
        if value_h == None or value_h == None:
            value_h, value_a = self.get_odd_values(value_type=value_type, stat_type=stat_type, period=period)
        if value_h: value_h = Decimal(value_h)
        if value_a: value_a = Decimal(value_a)
        return value_h, value_a

    def get_result(self):
        '''Method for obtaining the result of odd
           Reurining result and result_value
        '''
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    def calculate_result(self):
        if self.own_bet_type():
            #known bet_type
            odd = self
        else:
            #trasform common class Odd to end class
            cls = globals().get(self.bet_type.handler)
            if not cls: 
                raise ValueError('Unknonwn bet handler "%s"' % self.bet_type.handler)
            try:
                odd = cls.objects.get(pk=self.pk)
            except cls.DoesNotExist:
                raise ValueError('Cant find odd %s for bet handler "%s"' % (self.pk, bet_type.handler))

        result, result_value = odd.get_result()
        if result is not None and result_value is not None and result != Odd.UNKNOWN:
            if (self.result is None or self.result != result or 
                self.result_value is None or self.result_value != result_value or
                self.status != Odd.FINISHED
                ) :
                self.result = result
                self.result_value = result_value
                self.status = Odd.FINISHED
                self.result_update = timezone.now()
                self.save()

    def get_result_of_periods(self, period1, period2):
        #first half
        value_h1, value_a1 = self.get_odd_values(period=period1)
        value_h1 = get_int(value_h1)
        value_a1 = get_int(value_a1)
        #full time
        value_h2, value_a2 = self.get_odd_values(period=period2)
        value_h2 = get_int(value_h2)
        value_a2 = get_int(value_a2)
        return value_h1, value_a1, value_h2, value_a2

    def get_match_total(self, period=None, team=None, value_h=None, value_a=None):
        if value_h == None or value_h == None:
            value_h, value_a = self.get_odd_int_values(period=period)
        if value_h == None or value_a == None: total_value = None
        else:
            if team == None:
                team = self.team
            if not team: total_value = value_h + value_a
            elif team == Match.COMPETITOR_HOME: total_value = value_h
            elif team == Match.COMPETITOR_AWAY: total_value = value_a
            else:
                raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
        return total_value

    def get_result_by_value(self, value):
        if value == None:
            result = None
        elif value == 0:
            result = self.FAIL
        elif value < 1:
            result = self.PART_FAIL
        elif value == 1:
            result = self.RETURN
        elif value < self.odd_value:
            result = self.PART_SUCCESS
        else:
            result = self.SUCCESS
        return result

    def get_match_total_over_result(self, period=None, team=None, value_h=None, value_a=None):
        match_value = self.get_match_total(period=period, team=team, value_h=value_h, value_a=value_a)
        if match_value == None: result_value = None
        else:
            param_value = Decimal(self.param)
            result_value = get_total_over_result(param_value, match_value, self.odd_value)
        result = self.get_result_by_value(result_value)
        return result, result_value

    def get_match_total_under_result(self, period=None, team=None, value_h=None, value_a=None):
        match_value = self.get_match_total(period=period, team=team, value_h=value_h, value_a=value_a)
        if match_value == None: result_value = None
        else:
            param_value = Decimal(self.param)
            result_value = get_total_under_result(param_value, match_value, self.odd_value)
        result = self.get_result_by_value(result_value)
        return result, result_value

    def get_match_handicap(self, period=None, value_h=None, value_a=None):
        if value_h == None or value_a == None:
            value_h, value_a = self.get_odd_decimal_values(period=period)
        if value_h == None or value_a == None: handicap_value = None
        else:
            team = self.team
            if team == Match.COMPETITOR_HOME: handicap_value = value_h - value_a
            elif team == Match.COMPETITOR_AWAY: handicap_value = value_a - value_h
            else:
                raise ValueError('Invalid team param (should be "h" or "a"): %s' % team)
        return handicap_value

    def get_match_handicap_result(self, period=None, value_h=None, value_a=None):
        match_value = self.get_match_handicap(period=period, value_h=value_h, value_a=value_a)
        if match_value == None: 
            param_value = None
            result_value = None
        else:
            param_value = round(Decimal(self.param),5)
            result_value = get_handicap_result(param_value, match_value, self.odd_value)
        result = self.get_result_by_value(result_value)
        logger.debug('get_match_handicap_result param_value=%s result_value=%s result=%s' % (param_value,result_value,result))
        return result, result_value

    def get_margin_win(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: 
            win = None
            result = None
            result_value = None
        else:
            params = self.param.split(',')
            if not self.team: 
                win = (str(value_h - value_a) in(params) or str(value_a - value_h) in(params))
            elif self.team == Match.COMPETITOR_HOME:
                win = str(value_h - value_a) in(params) 
            elif self.team == Match.COMPETITOR_AWAY:
                win = str(value_a - value_h) in(params) 
            else:
                raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
        return win

    def calc_result_with_field_yes(self, win):
        if win == None:
            result = None
            result_value = None
        elif win == (self.yes=='Y'):
            result = self.SUCCESS
            result_value = self.odd_value
        else:
            result = self.FAIL
            result_value = 0
        return result, result_value

    def standard_forecasting(self, forecast_data, forecast_type="diff_team"):
        success_chance = float(0.0)
        lose_chance = float(0.0)
        result_value = float(0.0)
        fdata = None
        if forecast_data.__class__.__name__ == "dict":
            fdata = forecast_data.get(forecast_type, None)
            if not fdata and forecast_type != "simple":
                fdata = forecast_data.get("simple", None)
        else:
            fdata = forecast_data

        if fdata:   
            for data in fdata:
                result, value = self.get_result(value_h=data[0],value_a=data[1])
                v = float(value)
                d = float(data[2])
                result_value += (v*d)
                if value >= 1:
                    success_chance += d 
                    # if self.bet_type.slug == BetType.WIN_NO_BET:
                    #     print(data, round(success_chance,4), round(result_value,4), result, value)
                else: 
                    lose_chance += d
            result_value = Decimal(result_value)
        else:
            success_chance = None
            lose_chance = None
            result_value = None

        return success_chance, lose_chance, result_value


###################################################################
class VOdd(models.Model):

    id = models.IntegerField('pk', primary_key=True)

    period = models.IntegerField('Period')
    yes = models.CharField(r'Yes\No', max_length=1, choices=Odd.YES_CHOICES)
    team = models.CharField('Team', max_length=10, blank=True, choices=Odd.TEAM_CHOICES)
    param = models.CharField('Param', max_length=255, blank=True)
    odd_value = models.DecimalField('Odd', max_digits=10, decimal_places=3)
    status = models.CharField('Status', max_length=5, choices=Odd.STATUS_CHOICES)
    result = models.CharField('Result', max_length=5, choices=Odd.RESULT_CHOICES)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    odd_update = models.DateTimeField('Odd update', null=True, blank=True)
    result_update = models.DateTimeField('Result update', null=True, blank=True)

    bet_type_id = models.IntegerField('Bet type')
    bet_type_name = models.CharField('Bet type name', max_length=100)
    bet_type_description = models.CharField('Bet type description', max_length=2000, null=True, blank=True)
    bet_type_handler = models.CharField('Bet type handler', max_length=100, null=True, blank=True)

    bookie_id = models.IntegerField('Bookie')
    bookie_name = models.CharField('Bookie name', max_length=100)

    odd_bookie_config_id = models.IntegerField('Bookie Odd')
    odd_bookie_config_code = models.CharField('Bookie odd code', max_length=100)
    odd_bookie_config_name = models.CharField('Bookie odd name', max_length=255, null=True, blank=True)

    value_type_id = models.IntegerField('Value type')
    value_type_name = models.CharField('Value type name', max_length=100)

    load_source_id = models.IntegerField('Source')
    load_source_name = models.CharField('Load source name', max_length=100)

    match_id = models.IntegerField('Match')
    match_name = models.CharField('Match name', max_length=255, null=True, blank=True)
    match_date = models.DateField('Match date')
    match_result = models.CharField('Match result', max_length=5, choices=Match.RESULT_CHOICES, null=True, blank=True)
    score = models.CharField('Score', max_length=100, null=True, blank=True)
 
    league_id = models.IntegerField('League')
    league_name = models.CharField('League name', max_length=100)

    country_id = models.IntegerField('Country')
    country_code = models.CharField('Country Code', max_length=100)
    country_name = models.CharField('Country Name', max_length=100)

    team_h_id = models.IntegerField('Home team')
    team_h_name = models.CharField('Home Team Name', max_length=100)
    team_a_id = models.IntegerField('Away team')
    team_a_name = models.CharField('Away Team Name', max_length=100)

    class Meta:
        managed = False
        db_table = 'v_odd'


###################################################################
class OddWDL(OddMixins.WDLResult, OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.WDLParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WDL)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data, forecast_type="diff")
###################################################################
class OddWDLMinute(OddMixins.WDLResult, OddMixins.OnlyFootballMinutes, OddMixins.OnlyEmptyTeam, OddMixins.WDLParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WDL_MINUTE)
###################################################################
class OddResultHalf1Full(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.Double1X2Param, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.RESULT_HALF1_FULL)
    def get_result(self):
        value_h1, value_a1, value_h2, value_a2 = self.get_result_of_periods(period1=1,period2=0)
        if value_h1 == None or value_a1 == None or value_h2 == None or value_a2 == None: win = None
        else:
            params = self.param.split('/')
            win = (get_match_result(value_h1, value_a1)==params[0] and 
                   get_match_result(value_h2, value_a2)==params[1])
        return self.calc_result_with_field_yes(win)
###################################################################
class OddResultHalf1Half2(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.Double1X2Param, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.RESULT_HALF1_HALF2)
    def get_result(self):
        value_h1, value_a1, value_h2, value_a2 = self.get_result_of_periods(period1=1,period2=2)
        if value_h1 == None or value_a1 == None or value_h2 == None or value_a2 == None: win = None
        else:
            params = self.param.split('/')
            win = (get_match_result(value_h1, value_a1)==params[0] and 
                   get_match_result(value_h2, value_a2)==params[1])
        return self.calc_result_with_field_yes(win)
###################################################################
class OddWinBoth(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, OddMixins.EmptyParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WIN_BOTH)
    def get_result(self):
        value_h1, value_a1, value_h2, value_a2 = self.get_result_of_periods(period1=1,period2=2)
        if value_h1 == None or value_a1 == None or value_h2 == None or value_a2 == None: win = None
        else:
            team = self.team
            if not team:
                #any team
                win = ((value_h1 > value_a1) and (value_h2 > value_a2) or
                       (value_h1 < value_a1) and (value_h2 < value_a2)
                       )
            elif team == 'h':
                win = ((value_h1 > value_a1) and (value_h2 > value_a2))
            elif team == 'a':
                win = ((value_h1 < value_a1) and (value_h2 < value_a2))
            else:
                raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddWinLeastOneHalf(OddMixins.Only0Period, OddMixins.HomeOrAwayTeam, OddMixins.EmptyParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WIN_LEAST_ONE_HALF)
    def get_result(self):
        value_h1, value_a1, value_h2, value_a2 = self.get_result_of_periods(period1=1,period2=2)
        if value_h1 == None or value_a1 == None or value_h2 == None or value_a2 == None: win = None
        else:
            team = self.team
            if team == 'h':
                win = ((value_h1 > value_a1) or (value_h2 > value_a2))
            elif team == 'a':
                win = ((value_h1 < value_a1) or (value_h2 < value_a2))
            else:
                raise ValueError('Invalid team param (should be "h" or "a"): %s' % team)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddWinToNil(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.EmptyParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WIN_TO_NIL)
    def get_result(self, value_h=None, value_a=None):
        if value_h == None or value_a == None:
            value_h, value_a = self.get_odd_int_values()
        if value_h == None or value_a == None: win = None
        else:
            team = self.team
            if not team:
                #any team
                win = ((value_h > 0) and (value_a == 0) or
                       (value_a > 0) and (value_h == 0)
                       )
            elif team == 'h':
                win = ((value_h > 0) and (value_a == 0))
            elif team == 'a':
                win = ((value_a > 0) and (value_h == 0))
            else:
                raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddCorrectScore(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.ScoreListParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.CORRECT_SCORE)
    def get_result(self, value_h=None, value_a=None):
        if value_h == None or value_a == None:
            value_h, value_a = self.get_odd_values()
        if value_h != None and value_h.__class__.__name__ == "str": value_h = value_h.strip()
        if value_a != None and value_a.__class__.__name__ == "str": value_a = value_a.strip()
        if value_h == None or value_a == None: win = None
        else:
            score = '%s:%s' % (value_h, value_a)
            win = score in(self.param)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddTotalEvenOdd(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.EvenOddParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_EVEN_ODD)
    def get_result(self, value_h=None, value_a=None):
        total_value = self.get_match_total(value_h=value_h, value_a=value_a)
        if total_value == None: win = None
        else:
            if total_value % 2 == 0:
                #even
                win = (self.param == 'even')
            else:
                #odd
                win = (self.param == 'odd')
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddTotalOver(OddMixins.OnlyYes, OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.TotalParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        return self.get_match_total_over_result(value_h=value_h, value_a=value_a)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddTotalUnder(OddMixins.OnlyYes, OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.TotalParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        return self.get_match_total_under_result(value_h=value_h, value_a=value_a)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddTotalBothHalvesOver(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_BOTH_HALVES_OVER)
    def get_result(self):
        result_1, result_value_1 = self.get_match_total_over_result(period=1)
        result_2, result_value_2 = self.get_match_total_over_result(period=2)
        if result_1 == None or result_2 == None: win = None
        else:
            win = (result_1 == Odd.SUCCESS and result_2 == Odd.SUCCESS)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddTotalBothHalvesUnder(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_BOTH_HALVES_UNDER)
    def get_result(self):
        result_1, result_value_1 = self.get_match_total_under_result(period=1)
        result_2, result_value_2 = self.get_match_total_under_result(period=2)
        if result_1 == None or result_2 == None: win = None
        else:
            win = (result_1 == Odd.SUCCESS and result_2 == Odd.SUCCESS)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddTotalOverMinutes(OddMixins.OnlyYes, OddMixins.OnlyFootballMinutes, OddMixins.HomeAwayOrEmptyTeam, 
                            OddMixins.TotalParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_OVER_MINUTES)
    def get_result(self):
        return self.get_match_total_over_result()
###################################################################
class OddTotalUnderMinutes(OddMixins.OnlyYes, OddMixins.OnlyFootballMinutes, OddMixins.HomeAwayOrEmptyTeam, 
                            OddMixins.TotalParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL_UNDER_MINUTES)
    def get_result(self):
        return self.get_match_total_under_result()
###################################################################
class OddTotal(OddMixins.HomeAwayOrEmptyTeam, OddMixins.IntegerListParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TOTAL)
    def get_result(self, value_h=None, value_a=None):
        total_value = self.get_match_total(value_h=value_h, value_a=value_a)
        if total_value == None: win = None
        else:
            win = (str(total_value) in self.param.split(','))
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddHandicap(OddMixins.OnlyYes, OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HandicapParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.HANDICAP)
    def get_result(self, value_h=None, value_a=None):
        return self.get_match_handicap_result(value_h=value_h, value_a=value_a)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data, forecast_type="diff")
###################################################################
class OddHandicapMinutes(OddMixins.OnlyYes, OddMixins.OnlyFootballMinutes, OddMixins.HomeOrAwayTeam, 
                            OddMixins.HandicapParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.HANDICAP_MINUTES)
    def get_result(self):
        return self.get_match_handicap_result()
###################################################################
class OddConsecutiveGoals(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, OddMixins.PositiveIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.CONSECUTIVE_GOALS)
    def get_result(self):
        def get_next(i_h, i_a):
            if i_h == -1:
                i_h = 0; i_a = 0
            else:
                g_h = list_get(goals_h, i_h, 1000000)
                g_a = list_get(goals_a, i_a, 1000000)
                if g_h <= g_a: i_h += 1
                else: i_a += 1
            g_h = list_get(goals_h, i_h, 1000000)
            g_a = list_get(goals_a, i_a, 1000000)
            return i_h, i_a, g_h, g_a

        value_h, value_a = self.get_odd_values(stat_type=Match.GOAL_TIME, period=0)
        if value_h == None or value_a == None: win = None
        else:
            goals_h = [int(v) for v in value_h.split(',') if v] 
            goals_a = [int(v) for v in value_a.split(',') if v]
            N = int(self.param)
            team = self.team
            current_team = ''
            n = 0
            win = False
            i_h = -1
            i_a = -1
            i_h, i_a, g_h, g_a = get_next(i_h, i_a)
            while g_h < 1000000 or g_a < 1000000:
                t = Match.COMPETITOR_HOME if g_h <= g_a else Match.COMPETITOR_AWAY
                if t != current_team:
                    current_team = t
                    n = 1
                else:
                    n += 1
                if n >= N and (not team or team == current_team):
                    win = True
                    break
                # next loop
                i_h, i_a, g_h, g_a = get_next(i_h, i_a)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalBothOver(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_BOTH_OVER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_over_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_over_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            win = (result_h == Odd.SUCCESS and result_a == Odd.SUCCESS)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddITotalBothUnder(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_BOTH_UNDER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_under_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_under_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            win = (result_h == Odd.SUCCESS and result_a == Odd.SUCCESS)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddITotalOnlyOver(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_ONLY_OVER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_over_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_over_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            if self.team == Match.COMPETITOR_HOME:
                win = (result_h == Odd.SUCCESS and result_a != Odd.SUCCESS)
            elif self.team == Match.COMPETITOR_AWAY:
                win = (result_h != Odd.SUCCESS and result_a == Odd.SUCCESS)
            else:
                win =   (result_h == Odd.SUCCESS or result_a == Odd.SUCCESS)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddITotalOnlyUnder(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_ONLY_UNDER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_under_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_under_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            if self.team == Match.COMPETITOR_HOME:
                win = (result_h == Odd.SUCCESS and result_a != Odd.SUCCESS)
            elif self.team == Match.COMPETITOR_AWAY:
                win = (result_h != Odd.SUCCESS and result_a == Odd.SUCCESS)
            else:
                win =   (
                        (result_h == Odd.SUCCESS and result_a != Odd.SUCCESS) 
                        or
                        (result_h != Odd.SUCCESS and result_a == Odd.SUCCESS)
                        )
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddITotalAtLeastOver(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_AT_LEAST_OVER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_over_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_over_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            win = (result_h == Odd.SUCCESS or result_a == Odd.SUCCESS) 
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddITotalAtLeastUnder(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_AT_LEAST_UNDER)
    def get_result(self, value_h=None, value_a=None):
        result_h, result_value_h = self.get_match_total_under_result(team=Match.COMPETITOR_HOME, value_h=value_h, value_a=value_a)
        result_a, result_value_a = self.get_match_total_under_result(team=Match.COMPETITOR_AWAY, value_h=value_h, value_a=value_a)
        if result_h == None or result_a == None: win = None
        else:
            win = (result_h == Odd.SUCCESS or result_a == Odd.SUCCESS) 
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddMargin(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.IntegerListParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.MARGIN)
    def get_result(self, value_h=None, value_a=None):
        win = self.get_margin_win(value_h=value_h, value_a=value_a)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data, forecast_type="diff")
###################################################################
class OddWAndTotalOver(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.W_AND_TOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_over_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            if self.team == 'h':
                win = ((value_h > value_a) and (result == self.SUCCESS))
            elif self.team == 'a':
                win = ((value_h < value_a) and (result == self.SUCCESS))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWAndTotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.W_AND_TOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_under_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            if self.team == 'h':
                win = ((value_h > value_a) and (result == self.SUCCESS))
            elif self.team == 'a':
                win = ((value_h < value_a) and (result == self.SUCCESS))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWDAndTotalOver(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WD_AND_TOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_over_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            if self.team == 'h':
                win = ((value_h >= value_a) and (result == self.SUCCESS))
            elif self.team == 'a':
                win = ((value_h <= value_a) and (result == self.SUCCESS))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWDAndTotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WD_AND_TOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_under_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            if self.team == 'h':
                win = ((value_h >= value_a) and (result == self.SUCCESS))
            elif self.team == 'a':
                win = ((value_h <= value_a) and (result == self.SUCCESS))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddBothToScoreAndTotalOver(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.BOTH_TO_SCORE_AND_TOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_over_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            win = ((value_h > 0) and (value_a > 0) and (result == self.SUCCESS))
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddBothToScoreAndTotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.BOTH_TO_SCORE_AND_TOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_under_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            win = ((value_h > 0) and (value_a > 0) and (result == self.SUCCESS))
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddNotBothToScoreAndTotalOver(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_over_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            win = ((value_h == 0) or (value_a == 0)) and (result == self.SUCCESS)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddNotBothToScoreAndTotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        result, result_value = self.get_match_total_under_result(team='', value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            win = ((value_h == 0) or (value_a == 0)) and (result == self.SUCCESS)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWDLAndBothTeamsScore(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.WDLParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WDL_AND_BOTH_TEAMS_SCORE)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        elif self.param == 'w': win = (value_h > value_a) and (value_h > 0) and (value_a > 0)
        elif self.param == 'd': win = (value_h == value_a) and (value_h > 0) and (value_a > 0)
        elif self.param == 'l': win = (value_h < value_a) and (value_h > 0) and (value_a > 0)
        elif self.param == 'wd': win = (value_h >= value_a) and (value_h > 0) and (value_a > 0)
        elif self.param == 'dl': win = (value_h <= value_a) and (value_h > 0) and (value_a > 0)
        elif self.param == 'wl': win = (value_h != value_a) and (value_h > 0) and (value_a > 0)
        else: 
            raise ValueError('Invalid odd param (expected: w,d,l,wd,dl,wl): %s' % self.param)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddBothToScoreAt1_2(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.Two0or1Param, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.BOTH_TO_SCORE_AT_1_2)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        elif self.param == '0\\0': win = (value1_h == 0 or value1_a == 0) and (value2_h == 0 or value2_a == 0)
        elif self.param == '0\\1': win = (value1_h == 0 or value1_a == 0) and (value2_h > 0 and value2_a > 0)
        elif self.param == '1\\0': win = (value1_h > 0 and value1_a > 0) and (value2_h == 0 or value2_a == 0)
        elif self.param == '1\\1': win = (value1_h > 0 and value1_a > 0) and (value2_h > 0 and value2_a > 0)
        else: 
            raise ValueError('Invalid odd param (expected: w,d,l,wd,dl,wl): %s' % self.param)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalBothOverInBothHalves(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_BOTH_OVER_IN_BOTH_HALVES)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            param = Decimal(self.param)
            win = (value1_h > param) and (value1_a > param) and (value2_h > param) and (value2_a > param)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalBothUnderInBothHalves(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_BOTH_UNDER_IN_BOTH_HALVES)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            param = Decimal(self.param)
            win = (value1_h < param) and (value1_a < param) and (value2_h < param) and (value2_a < param)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalOnlyOverInBothHalves(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_ONLY_OVER_IN_BOTH_HALVES)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value1_h > param) and (value2_h > param) and ((value1_a < param) or (value2_a < param))
            elif self.team == 'a':
                win = (value1_a > param) and (value2_a > param) and ((value1_h < param) or (value2_h < param))
            elif not self.team:
                #neither
                win = ((value1_h < param) or (value2_h < param)) and ((value1_a < param) or (value2_a < param))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalOnlyUnderInBothHalves(OddMixins.Only0Period, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_ONLY_UNDER_IN_BOTH_HALVES)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value1_h < param) and (value2_h < param) and ((value1_a > param) or (value2_a > param))
            elif self.team == 'a':
                win = (value1_a < param) and (value2_a < param) and ((value1_h > param) or (value2_h > param))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddITotalBothOverAndEitherWin(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.ITOTAL_BOTH_OVER_AND_EITHER_WIN)
    def get_result(self):
        value_h, value_a = self.get_odd_int_values()
        if value_h == None or value_a == None: win = None
        else:
            param = Decimal(self.param)
            win = (value_h > param) and (value_a > param) and (value_h != value_a)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddRaceToGoals(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.PositiveIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.RACE_TO_GOALS)
    def get_result(self):
        def get_next(i_h, i_a):
            if i_h == -1:
                i_h = 0; i_a = 0
            else:
                g_h = list_get(goals_h, i_h, 1000000)
                g_a = list_get(goals_a, i_a, 1000000)
                if g_h <= g_a: i_h += 1
                else: i_a += 1
            g_h = list_get(goals_h, i_h, 1000000)
            g_a = list_get(goals_a, i_a, 1000000)
            return i_h, i_a, g_h, g_a

        value_h, value_a = self.get_odd_values(stat_type=Match.GOAL_TIME, period=0)
        if value_h == None or value_a == None: win = None
        else:
            goals_h = [int(v) for v in value_h.split(',') if v] 
            goals_a = [int(v) for v in value_a.split(',') if v]
            N = int(self.param)
            team = self.team
            current_team = ''
            n_h = 0
            n_a = 0
            win = not bool(team)
            i_h = -1
            i_a = -1
            i_h, i_a, g_h, g_a = get_next(i_h, i_a)
            while g_h < 1000000 or g_a < 1000000:
                if g_h <= g_a:
                    g = g_h
                    current_team = Match.COMPETITOR_HOME
                else:
                    g = g_a
                    current_team = Match.COMPETITOR_AWAY
                #goal did not score in period - skip
                if self.period == 0 or self.period == 1 and g <= 45 or self.period == 2 and g > 45:
                    if current_team == Match.COMPETITOR_HOME:
                        n_h += 1
                    else:
                        n_a += 1
                    if n_h >= N or n_a >= N:
                        if team == Match.COMPETITOR_HOME:
                            win = (n_h >= N)
                        elif team == Match.COMPETITOR_AWAY:
                            win = (n_a >= N)
                        else:
                            win = False
                        break
                # next loop
                i_h, i_a, g_h, g_a = get_next(i_h, i_a)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddHalfToScoreFirstGoal(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, Odd):
    class Meta:
        proxy = True
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if not param_ in('1','2'):
            raise ValueError('Invalid odd param (should 1 or 2): %s' % param)
        return param_
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.HALF_TO_SCORE_FIRST_GOAL)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            if self.team == Match.COMPETITOR_HOME:
                win = (self.param == '1' and value1_h > 0) or (self.param == '2' and value1_h == 0 and value2_h > 0)
            elif self.team == Match.COMPETITOR_AWAY:
                win = (self.param == '1' and value1_a > 0) or (self.param == '2' and value1_a == 0 and value2_a > 0)
            else:
                win = ((self.param == '1' and value1_h+value1_a > 0) or 
                       (self.param == '2' and value1_h+value1_a == 0 and value2_h+value2_a > 0))
        return self.calc_result_with_field_yes(win)
###################################################################
class OddTimeToScoreFirstGoal(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, Odd):
    class Meta:
        proxy = True
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if not param_ in('15','30','45','60','75','90'):
            raise ValueError('Invalid odd param (should be 15,30,45,60,75 or 90): %s' % param)
        return param_
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.TIME_TO_SCORE_FIRST_GOAL)
    def get_result(self):
        def get_next(i_h, i_a):
            if i_h == -1:
                i_h = 0; i_a = 0
            else:
                g_h = list_get(goals_h, i_h, 1000000)
                g_a = list_get(goals_a, i_a, 1000000)
                if g_h <= g_a: i_h += 1
                else: i_a += 1
            g_h = list_get(goals_h, i_h, 1000000)
            g_a = list_get(goals_a, i_a, 1000000)
            return i_h, i_a, g_h, g_a

        value_h, value_a = self.get_odd_values(stat_type=Match.GOAL_TIME, period=0)
        if value_h == None or value_a == None: win = None
        else:
            goals_h = [int(v) for v in value_h.split(',') if v] 
            goals_a = [int(v) for v in value_a.split(',') if v]
            team = self.team
            current_team = ''
            win = False
            i_h = -1
            i_a = -1
            i_h, i_a, g_h, g_a = get_next(i_h, i_a)
            while g_h < 1000000 or g_a < 1000000:
                if g_h <= g_a:
                    g = int(g_h)
                    current_team = Match.COMPETITOR_HOME
                else:
                    g = int(g_a)
                    current_team = Match.COMPETITOR_AWAY
                if not team or team == current_team:
                    #found first goal
                    if self.param == '15':
                        win = (g <= 15)
                    elif self.param == '30':
                        win = (g > 15 and g <= 30)
                    elif self.param == '45':
                        win = (g > 30 and g <= 45)
                    elif self.param == '60':
                        win = (g > 45 and g <= 60)
                    elif self.param == '75':
                        win = (g > 60 and g <= 75)
                    elif self.param == '90':
                        win = (g > 75 and g <= 90)
                    else:
                        raise ValueError('Invalid param (should be 15,30,45,60,75 or 90): %s' % self.param)
                    break
                # next loop
                i_h, i_a, g_h, g_a = get_next(i_h, i_a)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddDrawInEitherHalf(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.EmptyParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.DRAW_IN_EITHER_HALF)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            win = (value1_h == value1_a) or (value2_h == value2_a)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddHighestValueHalf(OddMixins.Only0Period, OddMixins.HomeAwayOrEmptyTeam, Odd):
    class Meta:
        proxy = True
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().lower()
        if param_ == "d":
            param_ = "x"
        if not param_ in('1','x','2'):
            raise ValueError('Invalid odd param (should be 1,x or 2): %s' % param)
        return param_
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.HIGHEST_VALUE_HALF)
    def get_result(self):
        value1_h, value1_a = self.get_odd_int_values(period=1)
        value2_h, value2_a = self.get_odd_int_values(period=2)
        if value1_h == None or value1_a == None or value2_h == None or value2_a == None: win = None
        else:
            if self.team == Match.COMPETITOR_HOME:
                value1 = value1_h
                value2 = value2_h
            elif self.team == Match.COMPETITOR_AWAY:
                value1 = value1_a
                value2 = value2_a
            else:
                value1 = value1_h + value1_a
                value2 = value2_h + value2_a
            if self.param == '1':
                win = (value1 > value2)
            elif self.param == 'x':
                win = (value1 == value2)
            elif self.param == '2':
                win = (value1 < value2)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddWinNoBet(OddMixins.OnlyYes, OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, Odd):
    class Meta:
        proxy = True
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().lower()
        if not param_ in('w','d'):
            raise ValueError('Invalid odd param (should be w or d): %s' % param)
        return param_
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WIN_NO_BET)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: result_value = None
        else:
            if self.team == Match.COMPETITOR_HOME:
                if value_h > value_a:
                    result_value = 1
                elif self.param == 'w':
                    result_value = self.odd_value if value_a > value_h else 0
                elif self.param == 'd':
                    result_value = self.odd_value if value_a == value_h else 0
                else:
                    raise ValueError('Invalid odd param (should be w or d): %s' % param)
            else:
                if value_h < value_a:
                    result_value = 1
                elif self.param == 'w':
                    result_value = self.odd_value if value_h > value_a else 0
                elif self.param == 'd':
                    result_value = self.odd_value if value_h == value_a else 0
                else:
                    raise ValueError('Invalid odd param (should be w or d): %s' % param)
        result = self.get_result_by_value(result_value)
        return result, result_value
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
# class OddDrawLeastOneHalf(Odd):
#     class Meta:
#         proxy = True
#     @staticmethod
#     def own_bet_type():
#         return BetType.get(BetType.DRAW_LEAST_ONE_HALF)
###################################################################
class OddWAndITotalOver(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.W_AND_ITOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value_h > value_a) and (value_h > param)
            elif self.team == 'a':
                win = (value_h < value_a) and (value_a > param)
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWAndITotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.W_AND_ITOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value_h > value_a) and (value_h < param)
            elif self.team == 'a':
                win = (value_h < value_a) and (value_a < param)
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWDAndITotalOver(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WD_AND_ITOTAL_OVER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value_h >= value_a) and (value_h > param)
            elif self.team == 'a':
                win = (value_h <= value_a) and (value_a > param)
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWDAndITotalUnder(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.HalfIntegerParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.WD_AND_ITOTAL_UNDER)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            param = Decimal(self.param)
            if self.team == 'h':
                win = (value_h >= value_a) and (value_h < param)
            elif self.team == 'a':
                win = (value_h <= value_a) and (value_a < param)
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
class OddWAndTotal(OddMixins.OnlyMatchPeriod, OddMixins.HomeOrAwayTeam, OddMixins.IntegerListParam, Odd):
    class Meta:
        proxy = True
    @staticmethod
    def own_bet_type():
        return BetType.get(BetType.W_AND_TOTAL)
    def get_result(self, value_h=None, value_a=None):
        value_h, value_a = self.get_odd_int_values(value_h=value_h, value_a=value_a)
        if value_h == None or value_a == None: win = None
        else:
            total_value = str(value_h + value_a)
            if self.team == 'h':
                win = (value_h > value_a) and (total_value in self.param.split(','))
            elif self.team == 'a':
                win = (value_h < value_a) and (total_value in self.param.split(','))
            else:
                raise ValueError('Invalid team param (should be "h", "a"): %s' % self.team)
        return self.calc_result_with_field_yes(win)
    def forecasting(self, forecast_data):
        return self.standard_forecasting(forecast_data)
###################################################################
# class OddPenaltyAndRCard(Odd):
#     class Meta:
#         proxy = True
#     @staticmethod
#     def own_bet_type():
#         return BetType.get(BetType.PENALTY_AND_R_CARD)
###################################################################
# class OddPenaltyOrRCard(Odd):
#     class Meta:
#         proxy = True
#     @staticmethod
#     def own_bet_type():
#         return BetType.get(BetType.PENALTY_OR_R_CARD)
###################################################################
# class OddYAndRCardsOver(Odd):
#     class Meta:
#         proxy = True
#     @staticmethod
#     def own_bet_type():
#         return BetType.get(BetType.Y_AND_R_CARDS_OVER)
###################################################################
# class OddYAndRCardsUnder(Odd):
#     class Meta:
#         proxy = True
#     @staticmethod
#     def own_bet_type():
#         return BetType.get(BetType.Y_AND_R_CARDS_UNDER)


