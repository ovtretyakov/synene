from datetime import datetime, date, timedelta
import logging

from django.utils import timezone

from core.models import Sport
from load.models import CommonHandler

logger = logging.getLogger(__name__)

###################################################################
class ESPNHandler(CommonHandler):

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return ESPNHandler.objects.get(
                        sport = Sport.objects.get(slug=Sport.FOOTBALL), 
                        slug=ESPNHandler.SRC_ESPN)
