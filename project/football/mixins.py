from core.factories import get_sport
from core.models import Sport

###################################################################
class FootballSaveMixin(object):
    def save(self, *args, **kwargs):
        if not self.sport_id:
            self.sport = get_sport(Sport.FOOTBALL)
        super(FootballSaveMixin, self).save(*args, **kwargs)

