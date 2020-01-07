from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from bootstrap_modal_forms.forms import BSModalForm

from .models import FootballLeague

######################################################################
class FootballLeagueForm(BSModalForm):

    class Meta:
        model = LoadSource
        fields = ["slug", "name", "team_type", "country", "load_status", "load_source",]



    # slug = models.SlugField()
    # name = models.CharField('League', max_length=100)
    # team_type = models.ForeignKey(TeamType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Team type')
    # sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    # country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')
    # load_status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='c')
    # load_source = models.ForeignKey('LoadSource', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Source',

