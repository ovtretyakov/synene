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

    @classmethod
    def get_or_create(cls, slug, **kwargs):
        kwargs.pop('sport',None)
        kwargs['sport']=Football.objects.get()
        return super(FootballLeague, cls).get_or_create(slug=slug, **kwargs)

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

