import os
from datetime import datetime, date, timedelta
from decimal import Decimal

from unittest import skip

from django.test import TestCase

from core.models import Country, League, Team, Match, MatchStats
from betting.models import BetType, ValueType, Odd, OddWDL, OddTotalOver, OddTotalUnder, OddHandicap
from load.models import ErrorLog
from load.handlers.espn import ESPNHandler 
from load.handlers.understat import UnderstatHandler
from load.handlers.football_data import FootballDataHandler

def prepare_data(obj):
    obj.handler = ESPNHandler.get()


#######################################################################################
######  ESPNHandler
#######################################################################################
class ESPNHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_espn_handler_get(self):
        handler = ESPNHandler.get()
        self.assertEquals(handler.slug, ESPNHandler.SRC_ESPN)


    #######################################################################
    def test_espn_process_debug_file(self):
        England = Country.get_object('eng')
        self.assertIsNotNone(England)
        Germany = Country.get_object('deu')
        self.assertIsNotNone(Germany)
        Scotland = Country.get_object('sco')
        self.assertIsNotNone(Scotland)
        load_date = date(2019,2,2)

        self.handler.process(is_debug=True, get_from_file=True, start_date=load_date)

        #English Premier League
        premier_league = League.objects.get(name= 'English Premier League', load_source=self.handler)
        self.assertEquals(premier_league.name, 'English Premier League')
        self.assertEquals(premier_league.country, England)
        premier_league_season = premier_league.get_season(load_date)
        self.assertEquals(premier_league_season.name, r'2018\2019')
        self.assertEquals(premier_league_season.start_date, date(2018,8,10))
        self.assertEquals(premier_league_season.end_date, date(2019,5,12))
        match_cnt = Match.objects.filter(league=premier_league, match_date=load_date).count()
        self.assertEquals(match_cnt, 7)
        
        #Tottenham Hotspur - Newcastle United
        Tottenham = Team.objects.get(name='Tottenham Hotspur')
        self.assertEquals(Tottenham.slug, 'tottenham-hotspur')
        self.assertEquals(Tottenham.country, England)
        self.assertIsNone(Tottenham.get_season(date(2018,8,1)))
        self.assertEquals(Tottenham.get_season(load_date), premier_league_season)
        Newcastle = Team.objects.get(name='Newcastle United')
        self.assertEquals(Newcastle.slug, 'newcastle-united')
        self.assertEquals(Newcastle.country, England)
        self.assertEquals(Newcastle.get_season(load_date), premier_league_season)
        
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=Tottenham,
                    team_a=Newcastle)
        self.assertEquals(str(match1), 'Tottenham Hotspur - Newcastle United')
        self.assertEquals(match1.score, '1:0 (0:0,1:0)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.WIN)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '83')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '8')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '2')
        #CORNERS
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '3')
        #FOULS
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '6')
        #POSSESSION
        self.assertEquals(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0), '71.600')
        self.assertEquals(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0), '28.400')

        #Brighton & Hove Albion - Watford
        Brighton = Team.objects.get(name='Brighton & Hove Albion')
        self.assertEquals(Brighton.slug, 'brighton-hove-albion')
        self.assertEquals(Brighton.country, England)
        self.assertIsNone(Brighton.get_season(date(2018,8,1)))
        self.assertEquals(Brighton.get_season(load_date), premier_league_season)
        Watford = Team.objects.get(name='Watford')
        self.assertEquals(Watford.slug, 'watford')
        self.assertEquals(Watford.country, England)
        self.assertEquals(Watford.get_season(load_date), premier_league_season)

        match2 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=Brighton,
                    team_a=Watford)
        self.assertEquals(str(match2), 'Brighton & Hove Albion - Watford')
        self.assertEquals(match2.score, '0:0 (0:0,0:0)')
        self.assertEquals(match2.status, Match.FINISHED)
        self.assertEquals(match2.result, Match.DRAW)

        #GOALS
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '0')
        #RCARD
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match2.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '')
        self.assertEquals(match2.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '')
        #SHOTS
        self.assertEquals(match2.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match2.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '5')
        #SHOTS_ON_TARGET
        self.assertEquals(match2.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match2.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '0')
        #CORNERS
        self.assertEquals(match2.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '7')
        self.assertEquals(match2.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '0')
        #FOULS
        self.assertEquals(match2.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '15')
        self.assertEquals(match2.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '10')
        #POSSESSION
        self.assertEquals(match2.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0), '55.100')
        self.assertEquals(match2.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0), '44.900')

        #German Bundesliga
        bundesliga = League.objects.get(name= 'German Bundesliga', load_source=self.handler)
        self.assertEquals(bundesliga.name, 'German Bundesliga')
        self.assertEquals(bundesliga.country, Germany)
        bundesliga_season = bundesliga.get_season(load_date)
        self.assertEquals(bundesliga_season.start_date, date(2018,8,24))
        self.assertEquals(bundesliga_season.end_date, date(2019,5,18))
        match_cnt = Match.objects.filter(league=bundesliga, match_date=load_date).count()
        self.assertEquals(match_cnt, 6)
        
        #Schalke 04 - Borussia Monchengladbach
        Schalke = Team.objects.get(name='Schalke 04')
        self.assertEquals(Schalke.slug, 'schalke-04')
        self.assertEquals(Schalke.country, Germany)
        self.assertIsNone(Schalke.get_season(date(2018,8,1)))
        self.assertEquals(Schalke.get_season(load_date), bundesliga_season)
        BorussiaM = Team.objects.get(name='Borussia Monchengladbach')
        self.assertEquals(BorussiaM.slug, 'borussia-monchengladbach')
        self.assertEquals(BorussiaM.country, Germany)
        self.assertEquals(BorussiaM.get_season(load_date), bundesliga_season)
        
        match3 = Match.objects.get(
                    league=bundesliga,
                    match_date=load_date,
                    team_h=Schalke,
                    team_a=BorussiaM)
        self.assertEquals(str(match3), 'Schalke 04 - Borussia Monchengladbach')
        self.assertEquals(match3.score, '0:2 (0:0,0:2)')
        self.assertEquals(match3.status, Match.FINISHED)
        self.assertEquals(match3.result, Match.LOOSE)

        #GOALS
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match3.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '2')
        #YCARD
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match3.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '0')
        #RCARD
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match3.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match3.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '2')
        #YCARD_MINUTE
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '2')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match3.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '')
        self.assertEquals(match3.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '85,90')
        #SHOTS
        self.assertEquals(match3.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '10')
        self.assertEquals(match3.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '16')
        #SHOTS_ON_TARGET
        self.assertEquals(match3.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '9')
        #CORNERS
        self.assertEquals(match3.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '6')
        #FOULS
        self.assertEquals(match3.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '10')
        self.assertEquals(match3.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '10')
        #POSSESSION
        self.assertEquals(match3.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0), '37.900')
        self.assertEquals(match3.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0), '62.100')


        #Scottish Premiership
        scottish_premiership = League.objects.get(name= 'Scottish Premiership', load_source=self.handler)
        self.assertEquals(scottish_premiership.name, 'Scottish Premiership')
        self.assertEquals(scottish_premiership.country, Scotland)
        scottish_premiership_season = scottish_premiership.get_season(load_date)
        self.assertEquals(scottish_premiership_season.start_date, date(2018,8,4))
        self.assertEquals(scottish_premiership_season.end_date, date(2019,4,7))
        match_cnt = Match.objects.filter(league=scottish_premiership, match_date=load_date).count()
        self.assertEquals(match_cnt, 4)
        
        #Hibernian - Aberdeen
        Hibernian = Team.objects.get(name='Hibernian')
        self.assertEquals(Hibernian.slug, 'hibernian')
        self.assertEquals(Hibernian.country, Scotland)
        self.assertIsNone(Hibernian.get_season(date(2018,8,1)))
        self.assertEquals(Hibernian.get_season(load_date), scottish_premiership_season)
        Aberdeen = Team.objects.get(name='Aberdeen')
        self.assertEquals(Aberdeen.slug, 'aberdeen')
        self.assertEquals(Aberdeen.country, Scotland)
        self.assertEquals(Aberdeen.get_season(load_date), scottish_premiership_season)
        
        match4 = Match.objects.get(
                    league=scottish_premiership,
                    match_date=load_date,
                    team_h=Hibernian,
                    team_a=Aberdeen)
        self.assertEquals(str(match4), 'Hibernian - Aberdeen')
        self.assertEquals(match4.score, '1:2 (1:2,0:0)')
        self.assertEquals(match4.status, Match.FINISHED)
        self.assertEquals(match4.result, Match.LOOSE)

        #GOALS
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match4.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match4.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match4.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '1')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match4.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match4.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match4.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match4.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '9')
        self.assertEquals(match4.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '12,22')
        #SHOTS
        self.assertEquals(match4.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match4.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '6')
        #SHOTS_ON_TARGET
        self.assertEquals(match4.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match4.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '3')
        #CORNERS
        self.assertEquals(match4.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match4.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '2')
        #FOULS
        self.assertEquals(match4.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '16')
        self.assertEquals(match4.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '7')
        #POSSESSION
        self.assertEquals(match4.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0), '31.000')
        self.assertEquals(match4.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0), '69.000')


    #######################################################################
    @skip("Skip load html")
    def test_espn_process_site(self):
        Spain = Country.get_object('esp')
        self.assertIsNotNone(Spain)
        load_date = date(2019,2,9)

        # self.handler.process(is_debug=True, start_date=load_date)
        self.handler.process(is_debug=True, get_from_file=True, start_date=load_date, is_debug_path=False)

        #Spanish Primera División
        la_liga = League.objects.get(name= 'Spanish Primera División', load_source=self.handler)
        self.assertEquals(la_liga.name, 'Spanish Primera División')
        self.assertEquals(la_liga.country, Spain)
        la_liga_season = la_liga.get_season(load_date)
        self.assertEquals(la_liga_season.start_date, date(2018,8,17))
        self.assertEquals(la_liga_season.end_date, date(2019,5,19))
        match_cnt = Match.objects.filter(league=la_liga, match_date=load_date).count()
        self.assertEquals(match_cnt, 4)
        
        #Atletico Madrid - Real Madrid
        Atletico = Team.objects.get(name='Atletico Madrid')
        self.assertEquals(Atletico.slug, 'atletico-madrid')
        self.assertEquals(Atletico.country, Spain)
        self.assertIsNone(Atletico.get_season(date(2018,2,1)))
        self.assertEquals(Atletico.get_season(load_date), la_liga_season)
        Real = Team.objects.get(name='Real Madrid')
        self.assertEquals(Real.slug, 'real-madrid')
        self.assertEquals(Real.country, Spain)
        self.assertEquals(Real.get_season(load_date), la_liga_season)
        
        match1 = Match.objects.get(
                    league=la_liga,
                    match_date=load_date,
                    team_h=Atletico,
                    team_a=Real)
        self.assertEquals(str(match1), 'Atletico Madrid - Real Madrid')
        self.assertEquals(match1.score, '1:3 (1:2,0:1)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.LOOSE)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '4')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '2')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '3')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '2')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '25')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '16,42,74')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '11')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '11')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
        #CORNERS
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '4')
        #FOULS
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '16')
        #POSSESSION
        self.assertEquals(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0), '34.200')
        self.assertEquals(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0), '65.800')


    #######################################################################
    @skip("Skip load html")
    def test_espn_get_html(self):
        url = 'https://www.espn.com/soccer/scoreboard/_/league/all/date/20180202'
        file_name = 'test.html'
        html1 = self.handler.get_html(file_name, url=url)

        fname = self.handler.get_handler_dir().path('cache').path(file_name)
        html2 = open(fname, 'rb').read()
        self.assertEquals(html1.encode(), html2)

        html3 = self.handler.get_html('test.html', get_from_file=True, is_debug_path=False)
        self.assertEquals(html1.encode(), html3)

        os.remove(fname)



#######################################################################################
######  UnderstatHandler
#######################################################################################
class UnderstatHandlerTest(TestCase):

    def setUp(self):
        self.handler = UnderstatHandler.get()

    #######################################################################
    def test_understat_handler_get(self):
        handler = UnderstatHandler.get()
        self.assertEquals(handler.slug, UnderstatHandler.SRC_UNDERSTAT)


    ######################################################################0
        UnknownCountry = Country.get_object('na')
        self.assertIsNotNone(UnknownCountry)
        load_date = date(2018, 8, 10)

        source_session = self.handler.process(debug_level=2, get_from_file=True, start_date=load_date)        
        self.assertIsNotNone(source_session)
        error_count = ErrorLog.objects.filter(source_session=source_session).count()
        self.assertEquals(error_count, 0)

        #EPL
        premier_league = League.objects.get(name= 'EPL', load_source=self.handler)
        self.assertEquals(premier_league.name, 'EPL')
        self.assertEquals(premier_league.country, UnknownCountry)
        match_cnt = Match.objects.filter(league=premier_league, match_date=load_date).count()
        self.assertEquals(match_cnt, 1)
        
        #Tottenham Hotspur - Newcastle United
        Tottenham = Team.objects.get(name='Manchester United')
        self.assertEquals(Tottenham.country, UnknownCountry)
        Newcastle = Team.objects.get(name='Leicester')
        self.assertEquals(Newcastle.country, UnknownCountry)
        
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=Tottenham,
                    team_a=Newcastle)
        self.assertEquals(str(match1), 'Manchester United - Leicester')
        self.assertEquals(match1.score, '2:1 (1:0,1:1)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.WIN)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '1')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '3,83')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '90')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '8')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '13')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
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
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0), '1.512')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0), '1.737')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 1), '0.900')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 1), '0.200')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 2), '0.612')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 2), '1.537')
        #XG_MINUTE
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 15), '0.801')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 45), '0.099')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 60), '0.028')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 75), '0.076')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 90), '0.508')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 15), '0.022')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 30), '0.127')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 45), '0.051')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 60), '0.024')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 75), '0.112')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 90), '1.401')
        #DEEP
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_AWAY, 0), '10')
        #PPDA
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_HOME, 0), '15.833')
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_AWAY, 0), '11.461')

    #######################################################################
    @skip("Skip load html")
    def test_understat_process_site(self):
        UnknownCountry = Country.get_object('na')
        self.assertIsNotNone(UnknownCountry)
        load_date = date(2019, 4, 27)

        source_session = self.handler.process(debug_level=1, get_from_file=False, start_date=load_date)        
        # source_session = self.handler.process(debug_level=1, get_from_file=True, is_debug_path=False, start_date=load_date)        
        self.assertIsNotNone(source_session)
        error_count = ErrorLog.objects.filter(source_session=source_session).count()
        self.assertEquals(error_count, 0)

        #EPL
        premier_league = League.objects.get(name= 'EPL', load_source=self.handler)
        self.assertEquals(premier_league.name, 'EPL')
        self.assertEquals(premier_league.country, UnknownCountry)
        match_cnt = Match.objects.filter(league=premier_league, match_date=load_date).count()
        self.assertEquals(match_cnt, 6)
        
        #Southampton - Bournemouth
        Southampton = Team.objects.get(name='Southampton')
        self.assertEquals(Southampton.country, UnknownCountry)
        Bournemouth = Team.objects.get(name='Bournemouth')
        self.assertEquals(Bournemouth.country, UnknownCountry)
        
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=Southampton,
                    team_a=Bournemouth)
        self.assertEquals(str(match1), 'Southampton - Bournemouth')
        self.assertEquals(match1.score, '3:3 (1:2,2:1)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.DRAW)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '1')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '12,55,67')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '20,32,86')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '22')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '9')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '7')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '5')
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
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0), '2.968')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0), '2.63')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 1), '2.185')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 1), '1.047')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 2), '0.783')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 2), '1.583')
        #XG_MINUTE
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 15), '1.083')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 30), '1.102')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 60), '0.643')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 75), '0.099')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 90), '0.041')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 30), '0.516')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 45), '0.531')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 60), '0.026')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 75), '0.035')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 90), '1.522')
        #DEEP
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_HOME, 0), '9')
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_AWAY, 0), '4')
        #PPDA
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_HOME, 0), '7.8')
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_AWAY, 0), '12.5')



        ##### La Liga
        la_liga = League.objects.get(name= 'La liga', load_source=self.handler)
        self.assertEquals(la_liga.name, 'La liga')
        self.assertEquals(la_liga.country, UnknownCountry)
        match_cnt = Match.objects.filter(league=la_liga, match_date=load_date).count()
        self.assertEquals(match_cnt, 4)
        
        #Atletico Madrid - Real Valladolid
        atletico_madrid = Team.objects.get(name='Atletico Madrid')
        self.assertEquals(atletico_madrid.country, UnknownCountry)
        real_valladolid = Team.objects.get(name='Real Valladolid')
        self.assertEquals(real_valladolid.country, UnknownCountry)
        
        match1 = Match.objects.get(
                    league=la_liga,
                    match_date=load_date,
                    team_h=atletico_madrid,
                    team_a=real_valladolid)
        self.assertEquals(str(match1), 'Atletico Madrid - Real Valladolid')
        self.assertEquals(match1.score, '1:0 (0:0,1:0)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.WIN)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '0')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '2')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '66')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '13')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '13')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
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
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0), '0.511')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0), '0.588')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 1), '0.287')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 1), '0.081')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 2), '0.224')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 2), '0.507')
        #XG_MINUTE
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 15), '0.097')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 30), '0.19')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 60), '0.113')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 75), '0.111')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 15), '0.041')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 30), '0.04')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 60), '0.013')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 75), '0.113')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 90), '0.381')
        #DEEP
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_HOME, 0), '11')
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_AWAY, 0), '1')
        #PPDA
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_HOME, 0), '5.875')
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_AWAY, 0), '12.0')


        ##### Bundesliga
        bundesliga = League.objects.get(name= 'Bundesliga', load_source=self.handler)
        self.assertEquals(bundesliga.name, 'Bundesliga')
        self.assertEquals(bundesliga.country, UnknownCountry)
        match_cnt = Match.objects.filter(league=bundesliga, match_date=load_date).count()
        self.assertEquals(match_cnt, 6)
        
        #Borussia Dortmund - Schalke 04
        borussia_dortmund = Team.objects.get(name='Borussia Dortmund')
        self.assertEquals(borussia_dortmund.country, UnknownCountry)
        schalke_04 = Team.objects.get(name='Schalke 04')
        self.assertEquals(schalke_04.country, UnknownCountry)
        
        match1 = Match.objects.get(
                    league=bundesliga,
                    match_date=load_date,
                    team_h=borussia_dortmund,
                    team_a=schalke_04)
        self.assertEquals(str(match1), 'Borussia Dortmund - Schalke 04')
        self.assertEquals(match1.score, '2:4 (1:2,1:2)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.LOOSE)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '4')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '2')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '6')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 2), '4')
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(Match.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '2')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(Match.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '1')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '2')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(Match.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '2')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(Match.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_HOME, 0), '14,85')
        self.assertEquals(match1.get_stat(Match.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '18,28,62,86')
        #SHOTS
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '8')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '8')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
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
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0), '1.103')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0), '1.124')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 1), '0.489')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 1), '0.887')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 2), '0.614')
        self.assertEquals(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 2), '0.237')
        #XG_MINUTE
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 15), '0.306')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 30), '0.121')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 45), '0.062')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 60), '0.036')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_HOME, 90), '0.578')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 15), '0.059')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 30), '0.785')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 45), '0.043')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 60), '0.073')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 75), '0.036')
        self.assertEquals(match1.get_stat(Match.XG_MINUTE, Match.COMPETITOR_AWAY, 90), '0.128')
        #DEEP
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match1.get_stat(Match.DEEP, Match.COMPETITOR_AWAY, 0), '2')
        #PPDA
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_HOME, 0), '10.2778')
        self.assertEquals(match1.get_stat(Match.PPDA, Match.COMPETITOR_AWAY, 0), '11.25')



#######################################################################################
######  FootballDataHandler
#######################################################################################
class FootballDataHandlerTest(TestCase):

    def setUp(self):
        self.handler = FootballDataHandler.get()

    #######################################################################
    def test_understat_handler_get(self):
        handler = FootballDataHandler.get()
        self.assertEquals(handler.slug, FootballDataHandler.SRC_FOOTBALL_DATA)

    #######################################################################
    def test_understat_process_debug_file(self):
        EnglandCountry = Country.get_object('eng')
        self.assertIsNotNone(EnglandCountry)
        load_date = date(2018, 8, 10)

        source_session = self.handler.process(debug_level=2, get_from_file=True, start_date=load_date)        
        self.assertIsNotNone(source_session)
        error_count = ErrorLog.objects.filter(source_session=source_session).count()
        self.assertEquals(error_count, 0)

        #EPL
        premier_league = League.objects.get(name= 'England Premier League', load_source=self.handler)
        self.assertEquals(premier_league.country, EnglandCountry)
        match_cnt = Match.objects.filter(league=premier_league, match_date=load_date).count()
        self.assertEquals(match_cnt, 1)

        #Tottenham Hotspur - Newcastle United
        Tottenham = Team.objects.get(name='Man United')
        self.assertEquals(Tottenham.country, EnglandCountry)
        Newcastle = Team.objects.get(name='Leicester')
        self.assertEquals(Newcastle.country, EnglandCountry)
        
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=load_date,
                    team_h=Tottenham,
                    team_a=Newcastle)
        self.assertEquals(str(match1), 'Man United - Leicester')
        self.assertEquals(match1.score, '2:1 (1:0,1:1)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.WIN)

        #Referee
        referee = match1.get_referee()
        self.assertIsNotNone(referee)
        self.assertEquals(referee.name, 'A Marriner')

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '2')
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
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '8')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '13')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
        #CORNERS
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '5')
        #FOULS
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '11')
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '8')
        #POSSESSION
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0))
        #XG
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0))
        
        #Bet WDL - w
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.58'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.58'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.93'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('7.5'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet TOTAL_OVER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.03'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('2.03'))
        #Bet TOTAL_UNDER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.79'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="-0.75",team="h")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.70'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.PART_SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.35'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="+0.75",team="a")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.21'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.PART_FAIL)
        self.assertEquals(odd.result_value, Decimal('0.50'))

        #########################################################
        #Chelsea - Man United
        Chelsea = Team.objects.get(name='Chelsea')
        self.assertEquals(Chelsea.country, EnglandCountry)
        ManUnited = Team.objects.get(name='Man United')
        self.assertEquals(ManUnited.country, EnglandCountry)
        
        match_date = date(2018, 10, 20)
        match1 = Match.objects.get(
                    league=premier_league,
                    match_date=match_date,
                    team_h=Chelsea,
                    team_a=ManUnited)
        self.assertEquals(str(match1), 'Chelsea - Man United')
        self.assertEquals(match1.score, '2:2 (1:0,1:2)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.DRAW)

        #Referee
        referee = match1.get_referee()
        self.assertIsNotNone(referee)
        self.assertEquals(referee.name, 'M Dean')

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '2')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '5')
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
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match1.get_stat(Match.SHOTS, Match.COMPETITOR_AWAY, 0), '7')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(Match.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
        #CORNERS
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_HOME, 0), '5')
        self.assertEquals(match1.get_stat(Match.CORNERS, Match.COMPETITOR_AWAY, 0), '3')
        #FOULS
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_HOME, 0), '9')
        self.assertEquals(match1.get_stat(Match.FOULS, Match.COMPETITOR_AWAY, 0), '17')
        #POSSESSION
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.POSSESSION, Match.COMPETITOR_AWAY, 0))
        #XG
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.XG, Match.COMPETITOR_AWAY, 0))

        #Bet WDL - w
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.74'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.93'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('3.93'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('5.26'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet TOTAL_OVER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.78'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.78'))
        #Bet TOTAL_UNDER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.04'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="-1.00",team="h")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.27'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="+1.00",team="a")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.67'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.67'))

    #######################################################################
    @skip("Skip load html")
    def test_understat_process_site(self):
        EnglandCountry = Country.get_object('eng')
        self.assertIsNotNone(EnglandCountry)
        GreeceCountry = Country.get_object('grc')
        self.assertIsNotNone(GreeceCountry)
        RussiaCountry = Country.get_object('rus')
        self.assertIsNotNone(RussiaCountry)
        load_date = date(2017, 8, 9)

        source_session = self.handler.process(debug_level=1, get_from_file=False, start_date=load_date)        
        # source_session = self.handler.process(debug_level=1, get_from_file=True, is_debug_path=False, start_date=load_date)        
        self.assertIsNotNone(source_session)
        error_count = ErrorLog.objects.filter(source_session=source_session).count()
        self.assertEquals(error_count, 0)

        #CONFERENCE LEAGUE
        match_date = date(2017, 8, 15)
        conference_league = League.objects.get(name= 'England Conference', load_source=self.handler)
        self.assertEquals(conference_league.country, EnglandCountry)
        match_cnt = Match.objects.filter(league=conference_league, match_date=match_date).count()
        self.assertEquals(match_cnt, 12)

        #Solihull - Barrow
        Team1 = Team.objects.get(name='Solihull')
        self.assertEquals(Team1.country, EnglandCountry)
        Team2 = Team.objects.get(name='Barrow')
        self.assertEquals(Team2.country, EnglandCountry)
        
        match1 = Match.objects.get(
                    league=conference_league,
                    match_date=match_date,
                    team_h=Team1,
                    team_a=Team2)
        self.assertEquals(str(match1), 'Solihull - Barrow')
        self.assertEquals(match1.score, '3:3 (0:2,3:1)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.DRAW)

        #Referee
        referee = match1.get_referee()
        self.assertIsNotNone(referee)
        self.assertEquals(referee.name, 'C Pollard')

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2), '3')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1))
        #RCARD
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0), '1')
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
        
        #Bet WDL - w
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.97'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.76'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('3.76'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.97'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet TOTAL_OVER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.72'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.72'))
        #Bet TOTAL_UNDER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.05'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="+0.50",team="h")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.90'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('1.90'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="-0.50",team="a")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.93'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))

        ################################################
        #GREECE LEAGUE
        match_date = date(2018, 2, 25)
        league = League.objects.get(name= 'Greece Ethniki Katigoria', load_source=self.handler)
        self.assertEquals(league.country, GreeceCountry)
        match_cnt = Match.objects.filter(league=league, match_date=match_date).count()
        self.assertEquals(match_cnt, 4)

        #PAOK - Olympiakos
        Team1 = Team.objects.get(name='PAOK')
        self.assertEquals(Team1.country, GreeceCountry)
        Team2 = Team.objects.get(name='Olympiakos')
        self.assertEquals(Team2.country, GreeceCountry)
        
        match1 = Match.objects.get(
                    league=league,
                    match_date=match_date,
                    team_h=Team1,
                    team_a=Team2)
        self.assertEquals(str(match1), 'PAOK - Olympiakos')
        self.assertEquals(match1.score, '0:3 (:,:)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.LOOSE)

        #Referee
        referee = match1.get_referee()
        self.assertIsNone(referee)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '3')
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2))
        #YCARD
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1))
        #RCARD
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0))
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
        
        #Bet WDL - w
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.79'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.33'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('5.86'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('5.86'))
        #Bet TOTAL_OVER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalOver.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.63'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('2.63'))
        #Bet TOTAL_UNDER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddTotalUnder.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.44'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="-0.50",team="h")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('1.74'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet HANDICAP
        odd = match1.get_odd(bet_type_slug=BetType.HANDICAP,param="+0.50",team="a")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddHandicap.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.09'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('2.09'))


        ###################################################
        #RUSSIA Premier League
        match_date = date(2017, 8, 9)
        league = League.objects.get(name= 'Russia Premier League', load_source=self.handler)
        self.assertEquals(league.country, RussiaCountry)
        match_cnt = Match.objects.filter(league=league, match_date=match_date).count()
        self.assertEquals(match_cnt, 5)

        #Rubin Kazan - Lokomotiv Moscow
        Team1 = Team.objects.get(name='Rubin Kazan')
        self.assertEquals(Team1.country, RussiaCountry)
        Team2 = Team.objects.get(name='Lokomotiv Moscow')
        self.assertEquals(Team2.country, RussiaCountry)
        
        match1 = Match.objects.get(
                    league=league,
                    match_date=match_date,
                    team_h=Team1,
                    team_a=Team2)
        self.assertEquals(str(match1), 'Rubin Kazan - Lokomotiv Moscow')
        self.assertEquals(match1.score, '1:1 (:,:)')
        self.assertEquals(match1.status, Match.FINISHED)
        self.assertEquals(match1.result, Match.DRAW)

        #Referee
        referee = match1.get_referee()
        self.assertIsNone(referee)

        #GOALS
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 0), '1')
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 1))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_HOME, 2))
        self.assertIsNone(match1.get_stat(Match.GOALS, Match.COMPETITOR_AWAY, 2))
        #YCARD
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 0))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_HOME, 1))
        self.assertIsNone(match1.get_stat(Match.YCARD, Match.COMPETITOR_AWAY, 1))
        #RCARD
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_HOME, 0))
        self.assertIsNone(match1.get_stat(Match.RCARD, Match.COMPETITOR_AWAY, 0))
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
        
        #Bet WDL - w
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="w")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('2.63'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet WDL - d
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="d")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.08'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.SUCCESS)
        self.assertEquals(odd.result_value, Decimal('3.08'))
        #Bet WDL - l
        odd = match1.get_odd(bet_type_slug=BetType.WDL,param="l")
        self.assertIsNotNone(odd)
        self.assertEquals(odd.__class__.__name__, OddWDL.__name__)
        self.assertEquals(odd.status, Odd.WAITING)
        self.assertEquals(odd.result, Odd.UNKNOWN)
        self.assertEquals(odd.odd_value, Decimal('3.13'))
        odd.calculate_result()
        self.assertEquals(odd.status, Odd.FINISHED)
        self.assertEquals(odd.result, Odd.FAIL)
        self.assertEquals(odd.result_value, Decimal('0'))
        #Bet TOTAL_OVER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_OVER,param="2.50")
        self.assertIsNone(odd)
        #Bet TOTAL_UNDER
        odd = match1.get_odd(bet_type_slug=BetType.TOTAL_UNDER,param="2.50")
        self.assertIsNone(odd)
