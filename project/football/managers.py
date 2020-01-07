from django.db import models

from project.core.factories import get_sport
from project.core.models import Sport

###################################################################
class FootballManager(models.Manager):
    ''' Football Manager '''

    def get_queryset(self):
        return super(FootballManager, self).get_queryset().filter(sport__slug=Sport.FOOTBALL)

    def create(self, **kwargs):
        football = get_sport(Sport.FOOTBALL)
        kwargs.update({'sport': football})
        return super(FootballManager, self).create(**kwargs)


###################################################################
class FootballSportManager(models.Manager):

    def get_queryset(self):
        return super(FootballSportManager, self).get_queryset().filter(slug=Sport.FOOTBALL)

