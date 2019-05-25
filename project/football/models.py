from .mixins import FootballSaveMixin
from .managers import FootballManager, FootballSportManager

from core.models import (
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
class FootballLeague(FootballSaveMixin, League):

    objects = FootballManager()


    class Meta:
        proxy = True


###################################################################
class FootballTeam(FootballSaveMixin, Team):

    objects = FootballManager()

    class Meta:
        proxy = True


###################################################################
class FootballReferee(FootballSaveMixin, Referee):

    objects = FootballManager()

    class Meta:
        proxy = True

