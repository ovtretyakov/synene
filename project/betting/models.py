import traceback

from django.db import models
from django.utils import timezone

from core.models import LoadSource, Match
from . import mixins as OddMixins
from core.utils import get_int, get_match_result

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
        CORNER:Match.CORENERS,
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
    DRAW_LEAST_ONE_HALF               = 'draw_least_one_half'
    W_AND_ITOTAL_OVER                 = 'w_and_itotal_over'
    W_AND_ITOTAL_UNDER                = 'w_and_itotal_under'
    WD_AND_ITOTAL_OVER                = 'wd_and_itotal_over'
    WD_AND_ITOTAL_UNDER               = 'wd_and_itotal_under'
    W_AND_TOTAL                       = 'w_and_total'
    PENALTY_AND_R_CARD                = 'penalty_and_r_card'
    PENALTY_OR_R_CARD                 = 'penalty_or_r_card'
    Y_AND_R_CARDS_OVER                = 'y_and_r_cards_over'
    Y_AND_R_CARDS_UNDER               = 'y_and_r_cards_under'


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
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, verbose_name='Bet type')
    period = models.IntegerField('Period', null=True, blank=True)
    param = models.CharField('Param', max_length=255, blank=True)
    team = models.CharField('Team', max_length=10, blank=True)
    yes = models.CharField(r'Yes\No', max_length=1)
    bookie_handler = models.CharField('Handler', max_length=100, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['bookie','code'], name='unique_odd_bookie_conf'),
        ]

    def __str__(self):
        return self.name


###################################################################
class Odd(models.Model):

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
    def create(cls, match, bet_type_slug, value_type_slug, load_source, bookie=None, 
                    period=0, yes='Y', team='', param='', odd_value=None, odd_bookie_config=None):
        # match
        if not match: raise ValueError('Missing parameter "match"')
        # bet_type
        if not bet_type_slug: raise ValueError('Missing parameter "bet_type_slug"')
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

        cls = globals().get(bet_type.handler)
        if not cls: 
            raise ValueError('Unknonwn bet handler "%s"' % bet_type.handler)
            # cls = Odd

        period = cls.clean_period(period)
        yes = cls.clean_yes(yes)
        team = cls.clean_team(team)
        param = cls.clean_param(param)
        odd_value = cls.clean_value(odd_value)

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

    @property
    def own_bet_type(self):
        return None

    @classmethod
    def clean_period(cls, period):
        if not period in(0,1,2,15,30,45,60,75,90,):
            raise ValueError('Invalid period param: %s' % period)
        return period

    @classmethod
    def clean_yes(cls, yes):
        if yes in('y','n'): yes = yes.upper()
        elif yes.lower() == 'yes': yes = 'Y'
        elif yes.lower() == 'no': yes = 'N'
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
        if value < 0:
            raise ValueError('Invalid bet value: %s' % value)
        return value

    def save(self, *args, **kwargs):
        if self.own_bet_type:
            self.bet_type = self.own_bet_type
        super(Odd, self).save(*args, **kwargs)

    def get_match_values(self, value_type=None, period=None):
        if value_type: 
            value_type = ValueType.get(value_type)
        else:
            value_type = self.value_type
        if period == None:
            period = self.period
        stat_type = value_type.get_stat_type()
        return self.match.get_competitors_values(stat_type, period)

    def get_odd_values(self, value_type=None, period=None):
        '''default method implementation'''
        return self.get_match_values(value_type=value_type, period=period)

    def get_odd_int_values(self, value_type=None, period=None):
        value_h, value_a = self.get_odd_values(value_type=value_type, period=period)
        if value_h: value_h = int(value_h)
        if value_a: value_a = int(value_a)
        return value_h, value_a

    def get_result(self):
        '''Method for obtaining the result of odd
           Reurining result and result_value
        '''
        raise NotImplementedError("Subclasses should implement this")

    def calculate_result(self):
        if self.status == Odd.WAITING:
            #only in waiting status
            #if not - just skip
            result, result_value = self.get_result()
            if result != None and result_value != None and result != Odd.UNKNOWN:
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


###################################################################
class OddWDL(OddMixins.WDLResult, OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.WDLParam, Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WDL)
###################################################################
class OddWDLMinute(OddMixins.WDLResult, OddMixins.OnlyFootballMinutes, OddMixins.OnlyEmptyTeam, OddMixins.WDLParam, Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WDL_MINUTE)
###################################################################
class OddResultHalf1Full(OddMixins.Only0Period, OddMixins.OnlyEmptyTeam, OddMixins.Double1X2Param, Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
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
    @property
    def own_bet_type(self):
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
    @property
    def own_bet_type(self):
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
    @property
    def own_bet_type(self):
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
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WIN_TO_NIL)
    def get_result(self):
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
###################################################################
class OddCorrectScore(OddMixins.OnlyMatchPeriod, OddMixins.OnlyEmptyTeam, OddMixins.ScoreListParam, Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.CORRECT_SCORE)
    def get_result(self):
        value_h, value_a = self.get_odd_values()
        if value_h == None or value_a == None: win = None
        else:
            score = '%s:%s' % (value_h.strip(), value_a.strip())
            win = score in(self.param)
        return self.calc_result_with_field_yes(win)
###################################################################
class OddTotalEvenOdd(OddMixins.OnlyMatchPeriod, OddMixins.HomeAwayOrEmptyTeam, OddMixins.EvenOddParam, Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_EVEN_ODD)
    def get_result(self):
        value_h, value_a = self.get_odd_int_values()
        if value_h == None or value_a == None: win = None
        else:
            team = self.team
            if not team: total = value_h + value_a
            elif team == Match.COMTETITOR_HOME: total = value_h
            elif team == Match.COMTETITOR_AWAY: total = value_a
            else:
                raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
            if total % 2 == 0:
                #even
                win = (self.param == 'even')
            else:
                #odd
                win = (self.param == 'odd')
        return self.calc_result_with_field_yes(win)
###################################################################
class OddTotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_OVER)
###################################################################
class OddTotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_UNDER)
###################################################################
class OddTotalBothHalvesOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_BOTH_HALVES_OVER)
###################################################################
class OddTotalBothHalvesUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_BOTH_HALVES_UNDER)
###################################################################
class OddTotalOverMinutes(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_OVER_MINUTES)
###################################################################
class OddTotalUnderMinutes(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL_UNDER_MINUTES)
###################################################################
class OddTotal(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.TOTAL)
###################################################################
class OddHandicap(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.HANDICAP)
###################################################################
class OddHandicapMinutes(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.HANDICAP_MINUTES)
###################################################################
class OddConsecutiveGoals(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.CONSECUTIVE_GOALS)
###################################################################
class OddITotalBothOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_BOTH_OVER)
###################################################################
class OddITotalBothUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_BOTH_UNDER)
###################################################################
class OddITotalOnlyOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_ONLY_OVER)
###################################################################
class OddITotalOnlyUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_ONLY_UNDER)
###################################################################
class OddITotalAtLeastOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_AT_LEAST_OVER)
###################################################################
class OddITotalAtLeastUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.ITOTAL_AT_LEAST_UNDER)
###################################################################
class OddMargin(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.MARGIN)
###################################################################
class OddWAndTotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.W_AND_TOTAL_OVER)
###################################################################
class OddWAndTotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.W_AND_TOTAL_UNDER)
###################################################################
class OddWDAndTotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WD_AND_TOTAL_OVER)
###################################################################
class OddWDAndTotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WD_AND_TOTAL_UNDER)
###################################################################
class OddBothToScoreAndTotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.BOTH_TO_SCORE_AND_TOTAL_OVER)
###################################################################
class OddBothToScoreAndTotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.BOTH_TO_SCORE_AND_TOTAL_UNDER)
###################################################################
class OddNotBothToScoreAndTotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_OVER)
###################################################################
class OddNotBothToScoreAndTotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER)
###################################################################
class OddWDLAndBothTeamsScore(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.WDL_AND_BOTH_TEAMS_SCORE)
###################################################################
class OddBothToScoreAt1_2(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(BetType.BOTH_TO_SCORE_AT_1_2)
###################################################################
class OddITotalBothOverInBothHalves(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(ITOTAL_BOTH_OVER_IN_BOTH_HALVES)
###################################################################
class OddITotalBothUnderInBothHalves(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(ITOTAL_BOTH_UNDER_IN_BOTH_HALVES)
###################################################################
class OddITotalOnlyOverInBothHalves(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(ITOTAL_ONLY_OVER_IN_BOTH_HALVES)
###################################################################
class OddITotalOnlyUnderInBothHalves(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(ITOTAL_ONLY_UNDER_IN_BOTH_HALVES)
###################################################################
class OddITotalBothOverAndEitherWin(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(ITOTAL_BOTH_OVER_AND_EITHER_WIN)
###################################################################
class OddRaceToGoals(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(RACE_TO_GOALS)
###################################################################
class OddHalfToScoreFirstGoal(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(HALF_TO_SCORE_FIRST_GOAL)
###################################################################
class OddTimeToScoreFirstGoal(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(TIME_TO_SCORE_FIRST_GOAL)
###################################################################
class OddDrawInEitherHalf(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(DRAW_IN_EITHER_HALF)
###################################################################
class OddHighestValueHalf(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(HIGHEST_VALUE_HALF)
###################################################################
class OddWinNoBet(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(WIN_NO_BET)
###################################################################
class OddDrawLeastOneHalf(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(DRAW_LEAST_ONE_HALF)
###################################################################
class OddWAndITotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(W_AND_ITOTAL_OVER)
###################################################################
class OddWAndITotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(W_AND_ITOTAL_UNDER)
###################################################################
class OddWDAndITotalOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(WD_AND_ITOTAL_OVER)
###################################################################
class OddWDAndITotalUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(WD_AND_ITOTAL_UNDER)
###################################################################
class OddWAndTotal(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(W_AND_TOTAL)
###################################################################
class OddPenaltyAndRCard(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(PENALTY_AND_R_CARD)
###################################################################
class OddPenaltyOrRCard(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(PENALTY_OR_R_CARD)
###################################################################
class OddYAndRCardsOver(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(Y_AND_R_CARDS_OVER)
###################################################################
class OddYAndRCardsUnder(Odd):
    class Meta:
        proxy = True
    @property
    def own_bet_type(self):
        return BetType.get(Y_AND_R_CARDS_UNDER)


