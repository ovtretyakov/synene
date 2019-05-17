import traceback

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError

from core.models import LoadSource, Match
from .mixins import WDLParamClean

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

    slug = models.SlugField(unique=True)
    name = models.CharField('Type', max_length=100)

    def __str__(self):
        return self.name


###################################################################
class BetType(models.Model):

    WDL = 'wdl'
    WDL_MINUTE = 'wdl_minute'

    slug = models.SlugField(unique=True)
    name = models.CharField('Type', max_length=100)
    description = models.CharField('Description', max_length=2000, null=True, blank=True)
    handler = models.CharField('Handler', max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


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
    def add(cls, match, bet_type_slug, value_type_slug, load_source, bookie=None, 
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
        except BetType.DoesNotExist:
            raise ValueError('Unknown value_type: %s' % value_type_slug)
        # load_source
        if not load_source: raise ValueError('Missing parameter "load_source"')
        # bookie
        if bookie and not bookie.is_betting: raise ValueError('"%s" is not betting source' % bookie)

        cls = globals().get(bet_type.handler)
        if not cls: cls = Odd

        period = cls.clean_period()
        yes = cls.clean_yes()
        team = cls.clean_team()
        param = cls.clean_param()
        odd_value = cls.clean_value()

        #if exists
        try:
            if bookie:
                odd = Odd.objects.select_related('load_source').get(
                                      match=match,bet_type=bet_type,bookie=bookie,value_type=value_type,
                                      period=period,yes=yes,team=team,param=param)
            else:
                odd = Odd.objects.select_related('load_source').get(
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
            odd = Odd.objects.create(
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
            ValidationError(_('Invalid period param: %(period)s'), params={'period': period},  code='invalid_period')
        return period

    @classmethod
    def clean_yes(cls, yes):
        if yes in('y','n'): yes = yes.upper()
        elif yes.lower() == 'yes': yes = 'Y'
        elif yes.lower() == 'no': yes = 'N'
        if not yes in('Y','N',):
            ValidationError(_('Invalid yes-no param: %(yes)s'), params={'yes': yes},  code='invalid_yes-no')
        return yes

    @classmethod
    def clean_team(cls, team):
        if team in('H','A'): team = team.lower()
        elif team.lower() == 'home': team = 'h'
        elif team.lower() == 'away': team = 'a'
        if not team in('h','a',):
            ValidationError(_('Invalid team param: %(team)s'), params={'team': team},  code='invalid_team')
        return team

    @classmethod
    def clean_param(cls, param):
        return param

    @classmethod
    def clean_value(cls, value):
        return value

    def save(self, *args, **kwargs):
        if self.own_bet_type:
            self.bet_type = own_bet_type
        super(Odd, self).save(*args, **kwargs)


###################################################################
class OddWDL(WDLParamClean, Odd):

    class Meta:
        proxy = True

    @property
    def own_bet_type(self):
        return BetType.WDL

