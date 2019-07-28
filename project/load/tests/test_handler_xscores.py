import os
from datetime import datetime, date, timedelta
from decimal import Decimal

from unittest import skip

from django.test import TestCase

from core.models import Country, League, Team, Match, MatchStats
from betting.models import BetType, ValueType, Odd, OddWDL, OddTotalOver, OddTotalUnder, OddHandicap
from load.models import ErrorLog
from load.handlers.xscores import XScoresHandler 

def prepare_data(obj):
    obj.handler = XScoresHandler.get()


#######################################################################################
######  XScoresHandler
#######################################################################################
class XScoresHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_espn_handler_get(self):
        handler = XScoresHandler.get()
        self.assertEquals(handler.slug, XScoresHandler.SRC_XSCORES)


    #######################################################################
    def test_espn_process_debug_file(self):
        England = Country.get_object('eng')
        self.assertIsNotNone(England)
        Germany = Country.get_object('deu')
        self.assertIsNotNone(Germany)
        Scotland = Country.get_object('sco')
        self.assertIsNotNone(Scotland)
        load_date = date(2019,2,27)

        source_session = self.handler.process(debug_level=1, get_from_file=True, start_date=load_date)
        self.assertIsNotNone(source_session)
        error_count = ErrorLog.objects.filter(source_session=source_session).count()
        self.assertEquals(error_count, 0)

        #EPL
        premier_league = League.objects.get(name= 'eng PREMIER LEAGUE', load_source=self.handler)
        self.assertEquals(premier_league.country, England)
        match_cnt = Match.objects.filter(league=premier_league, match_date=load_date).count()
        self.assertEquals(match_cnt, 6)

        #Chelsea - Tottenham
        team1 = Team.objects.get(name__iexact='Chelsea')
        self.assertEquals(team1.country, England)
        team2 = Team.objects.get(name__iexact='Tottenham')
        self.assertEquals(team2.country, England)
        
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=team1,
                    team_a=team2)
        self.assertEquals(str(match1), 'CHELSEA - TOTTENHAM')
        self.assertEquals(match1.score, '2:0 (0:0,2:0)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.WIN)

        #Referee
        referee = match1.get_referee()
        self.assertIsNotNone(referee)
        self.assertEquals(referee.name, 'Andre Marriner')

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '1')
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1))
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1))
        #PENALTY
        self.assertIsNone(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0))
        #GOALS_MINUTE
        self.assertIsNone(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15))
        self.assertIsNone(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15))
        #YCARD_MINUTE
        self.assertIsNone(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15))
        self.assertIsNone(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15))
        #RCARD_MINUTE
        self.assertIsNone(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15))
        self.assertIsNone(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15))
        #GOAL_TIME
        self.assertIsNone(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0))
        #SHOTS
        self.assertIsNone(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0))
        #SHOTS_ON_TARGET
        self.assertIsNone(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0))
        #CORNERS
        self.assertIsNone(match1.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0))
        #FOULS
        self.assertIsNone(match1.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0))
        #POSSESSION
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0))
        #XG
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0))
        
