from .mixins import FootballSaveMixin, FootballGetOrCreateMixin
from .managers import FootballManager, FootballSportManager

from project.core.models import (
    Sport,
    LoadSource,
    League,
    Team,
    Referee,
    )


###################################################################
class Football(Sport):

    objects = FootballSportManager()

    class Meta:
        proxy = True


###################################################################
class FootballSource(FootballSaveMixin, LoadSource):

    objects = FootballManager()

    class Meta:
        proxy = True


###################################################################
class FootballLeague(FootballGetOrCreateMixin, FootballSaveMixin, League):

    objects = FootballManager()


    class Meta:
        proxy = True


###################################################################
class FootballTeam(FootballGetOrCreateMixin, FootballSaveMixin, Team):

    objects = FootballManager()

    class Meta:
        proxy = True


###################################################################
class FootballReferee(FootballGetOrCreateMixin, FootballSaveMixin, Referee):

    objects = FootballManager()

    class Meta:
        proxy = True

