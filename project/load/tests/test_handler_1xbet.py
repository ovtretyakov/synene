import os
from datetime import datetime, date, timedelta
from decimal import Decimal

from unittest import skip

from django.test import TestCase
from django.test.utils import override_settings

from project.core.models import Country, League, Team, Match, MatchStats
from project.betting.models import BetType, ValueType, Odd, OddWDL, OddTotalOver, OddTotalUnder, OddHandicap
from ..models import ErrorLog
from ..handlers.xbet import XBetHandler 

def prepare_data(obj):
    obj.handler = XBetHandler.get()


#######################################################################################
######  XBetHandler
#######################################################################################
class XbetHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_1xbet_handler_get(self):
        handler = XBetHandler.get()
        self.assertEquals(handler.slug, XBetHandler.SRC_1XBET)

    #######################################################################
    def test_1xbet_process_debug_file(self):
        England = Country.get_object("eng")
        self.assertIsNotNone(England)

        self.handler.process(debug_level=2, get_from_file=True)

        league = League.objects.get(name__icontains= "Premier League", load_source=self.handler)
        self.assertEquals(league.name, "England. Premier League")
        self.assertEquals(league.country, England)

        Southampton = Team.objects.get(name="Southampton")
        Liverpool = Team.objects.get(name="Liverpool")
        match_date = date(2019, 4, 5)
        match1 = Match.objects.get(
                    league=league,
                    match_date=match_date,
                    team_h=Southampton,
                    team_a=Liverpool)
        self.assertEquals(str(match1), "Southampton - Liverpool")
        self.assertEquals(match1.status, Match.SCHEDULED)

        ####################################################################
        # WDL
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w",period=0)
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal("8.5"))
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal("4.98"))
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.425"))
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="wd",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal("3.155"))
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="wl",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.216"))
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="dl",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.104"))
        ####################################################################
        # TOTAL
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.76"))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal("2.232"))
        ####################################################################
        # HANDICAP
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="h",param="+1.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.78"))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="a",param="-1.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal("2.2"))
        ####################################################################
        # ITOTAL
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,team="h",param="0.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.74"))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,team="h",param="0.50",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal("2.09"))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,team="a",param="2.00",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.9"))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,team="a",param="2.00",period=0)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal("1.9"))


    #######################################################################
    def test_1xbet_load_file(self):
        # self.handler.process()
        self.handler.process(get_from_file=True, is_debug_path=False)
