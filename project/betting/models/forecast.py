import traceback
from decimal import Decimal
import logging

from django.db import models
from django.utils import timezone

from .betting import ValueType
from project.core.models import Sport, Match, League, Country, Team
from project.betting.models import Odd

logger = logging.getLogger(__name__)

################## Data prepartion ##################
class HarvestHandler(models.Model):

    slug = models.SlugField(unique=True)
    name = models.CharField('Harvest Type', max_length=100)
    param_descr = models.CharField('Parameter Description', max_length=1000, blank=True)
    handler = models.CharField('Handler', max_length=100, blank=True)

    def __str__(self):
        return self.name


class Harvest(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField('Script', max_length=100)
    comment = models.CharField('Comment', max_length=1000, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    harvest_handler = models.ForeignKey(HarvestHandler, on_delete=models.PROTECT, verbose_name='Harvest Type')
    value_type = models.ForeignKey(ValueType, on_delete=models.PROTECT, verbose_name='Vaue Type')
    period = models.IntegerField('Period')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')

    def __str__(self):
        return self.name


class HarvestConfig(models.Model):

    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    code = models.CharField('Code', max_length=100)
    value = models.CharField('Value', max_length=1000, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest','code'], name='unique_harvest_conf'),
        ]

    def __str__(self):
        return f'{self.harvest}:{self.code}:{self.value}'



class HarvestGroup(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField('Group', max_length=100)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')
    harvest_date = models.DateField('Harvest date', null=True, blank=True)
    last_update = models.DateTimeField('Last update', null=True, blank=True)

    def __str__(self):
        return self.name



class HarvestLeague(models.Model):

    harvest_group = models.ForeignKey(HarvestGroup, on_delete=models.CASCADE, verbose_name='Harvest Group')
    league = models.ForeignKey(League, on_delete=models.PROTECT, verbose_name='League')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest_group','league'], name='unique_harvest_league'),
        ]

    def __str__(self):
        return f'{self.harvest_group}:{self.league}'


class TeamSkill(models.Model):

    harvest_group = models.ForeignKey(HarvestGroup, on_delete=models.PROTECT, verbose_name='Harvest Group')
    team = models.ForeignKey(Team, on_delete=models.PROTECT, verbose_name='Team')
    event_date = models.DateField('Event date')
    match = models.ForeignKey(Match, on_delete=models.PROTECT, verbose_name='Match')
    match_cnt = models.IntegerField('Match Count')

    # values for calculations (log format)
    lvalue1  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue2  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue3  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue4  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue5  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue6  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue7  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue8  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue9  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue10 = models.DecimalField('LValue1', max_digits=10, decimal_places=5)

    # values for presentation
    value1  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value2  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value3  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value4  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value5  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value6  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value7  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value8  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value9  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value10 = models.DecimalField('LValue1', max_digits=10, decimal_places=5)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest_group','team','event_date','match'], name='unique_team_skill'),
        ]

    def __str__(self):
        return f'W:{self.harvest_group},T:{self.team},D:{self.event_date},M:{self.match}'




################## Forecast ##################
class ForecastHandler(models.Model):

    slug = models.SlugField(unique=True)
    name = models.CharField('Forecast Handler', max_length=100)
    handler = models.CharField('Handler', max_length=100, blank=True)

    def __str__(self):
        return self.name



class Predictor(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True)
    name = models.CharField('Predictor', max_length=100)
    comment = models.CharField('Comment', max_length=1000, blank=True)
    forecast_handler = models.ForeignKey(ForecastHandler, on_delete=models.PROTECT, verbose_name='Forecast Type')
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    priority = models.IntegerField('Priority')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')

    def __str__(self):
        return self.name




class Forecast(models.Model):

    set = models.CharField('Set', max_length=10, default='m')
    predictor = models.ForeignKey(Predictor, on_delete=models.PROTECT, verbose_name='Predictor')
    harvest = models.ForeignKey(Harvest, on_delete=models.PROTECT, verbose_name='Harvest')
    match = models.ForeignKey(Match, on_delete=models.PROTECT, verbose_name='Match')
    odd = models.ForeignKey(Odd, on_delete=models.PROTECT, verbose_name='Odd')
    success_chance  = models.DecimalField('LValue1', max_digits=10, decimal_places=3)
    lose_chance  = models.DecimalField('LValue1', max_digits=10, decimal_places=3)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    Kelly = models.DecimalField('Kelly', max_digits=10, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['set','odd','predictor'], name='unique_forecast'),
        ]

    def __str__(self):
        return f'S:{self.set},Odd:<{self.odd}>,P:{self.predictor},R:{self.result_value}'



