from core.factories import get_sport
from core.models import Sport

###################################################################
class FootballSaveMixin(object):
    def save(self, *args, **kwargs):
        if not self.sport_id:
            self.sport = get_sport(Sport.FOOTBALL)
        super(FootballSaveMixin, self).save(*args, **kwargs)


###################################################################
class FootballGetOrCreateMixin(object):
    @classmethod
    def get_or_create(cls, **kwargs):
        kwargs.pop('sport',None)
        kwargs['sport']=get_sport(Sport.FOOTBALL)
        return super(FootballGetOrCreateMixin, cls).get_or_create(**kwargs)
