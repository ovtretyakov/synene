import os
from datetime import datetime, date, timedelta
from decimal import Decimal

from unittest import skip

from django.test import TestCase
from django.test.utils import override_settings

from core.models import Country, League, Team, Match, MatchStats
from betting.models import BetType, ValueType, Odd, OddWDL, OddTotalOver, OddTotalUnder, OddHandicap
from load.models import ErrorLog
from load.handlers.parimatch import ParimatchHandler 

def prepare_data(obj):
    obj.handler = ParimatchHandler.get()


#######################################################################################
######  ParimatchHandler
#######################################################################################
class ParimatchHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_espn_handler_get(self):
        handler = ParimatchHandler.get()
        self.assertEquals(handler.slug, ParimatchHandler.SRC_PARIMATCH)

    #######################################################################
    # @override_settings(DEBUG=True)
    def test_parimatch_process_debug_file(self):
        UnknownCountry = Country.get_object('na')
        self.assertIsNotNone(UnknownCountry)
        Portugal = Country.get_object('prt')
        self.assertIsNotNone(Portugal)
        Italy = Country.get_object('ita')
        self.assertIsNotNone(Italy)
        now = datetime.now()

        self.handler.process(debug_level=2, get_from_file=True)

        #Football. UEFA Champions League
        uefa_league = League.objects.get(name__icontains= 'UEFA Champions', load_source=self.handler)
        self.assertEquals(uefa_league.name, 'Football. UEFA Champions League')
        self.assertEquals(uefa_league.country, UnknownCountry)
        match_cnt = Match.objects.filter(league=uefa_league).count()
        self.assertEquals(match_cnt, 6)

        #FC Porto - Roma
        Porto = Team.objects.get(name='FC Porto(PRT)')
        Roma = Team.objects.get(name='Roma(ITA)')
        match_date = date(now.year, 3, 6)
        match1 = Match.objects.get(
                    league=uefa_league,
                    match_date=match_date,
                    team_h=Porto,
                    team_a=Roma)
        self.assertEquals(str(match1), 'FC Porto(PRT) - Roma(ITA)')
        self.assertEquals(match1.status, Match.SCHEDULED)

        ####################################################################
        #Bet WDL - w
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w",period=0)
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.89'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal('3.9'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal('4'))
        #Bet WDL - wd
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="wd",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.27'))
        #Bet WDL - dl
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="dl",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.97'))
        #Bet WDL - wl
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="wl",period=0)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.28'))

        ####################################################################
        #Handicap
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="h",period=0,param="-1.00")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('2.60'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="a",period=0,param="+1.00")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.55'))
        #1st half
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="h",period=1,param="0")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.52'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="h",period=1,param="-1.50")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('6.9'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="h",period=1,param="-1.00")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('5.4'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="a",period=1,param="0")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('2.55'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="a",period=1,param="+1.50")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.1'))
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,team="a",period=1,param="+1.00")
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.15'))

        ####################################################################
        #Total_Over
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,period=0,param="2.50")
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.74'))

        ####################################################################
        #Total_Under
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,period=0,param="2.50")
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal('2.17'))

        ####################################################################
        #ITotal_Over
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,team="h",period=0,param="1.50")
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.81'))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,team="a",period=0,param="1.00")
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.88'))

        ####################################################################
        #ITotal_Under
        ####################################################################
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,team="h",period=0,param="1.50")
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal('2.00'))
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,team="a",period=0,param="1.00")
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.odd_value, Decimal('1.92'))
