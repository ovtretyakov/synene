import os
from datetime import datetime, date, timedelta
import logging

from django.utils import timezone

from load.models import CommonHandler

logger = logging.getLogger(__name__)




###################################################################
class FootballDataHandler(CommonHandler):

    DEBUG_DATE = date(1900, 1, 1)

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_FOOTBALL_DATA)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path('football_data') 
