import os
from datetime import datetime, date, timedelta

from unittest import skip

from django.test import TestCase

from core.models import Country, League, Team, Match, MatchStats
from load.handlers.espn import ESPNHandler


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
    def test_espn_process_degug_file(self):
        England = Country.get_object('eng')
        self.assertIsNotNone(England)
        Germany = Country.get_object('deu')
        self.assertIsNotNone(Germany)
        Scotland = Country.get_object('sco')
        self.assertIsNotNone(Scotland)
        load_date = date(2019,2,2)

        self.handler.process(is_debug=True, start_date=load_date)

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
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_HOME, 0), '83')
        self.assertEquals(match1.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '')
        #SHOTS
        self.assertEquals(match1.get_stat(MatchStats.SHOTS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match1.get_stat(MatchStats.SHOTS, Match.COMPETITOR_AWAY, 0), '8')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match1.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '2')
        #CORNERS
        self.assertEquals(match1.get_stat(MatchStats.CORNERS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(MatchStats.CORNERS, Match.COMPETITOR_AWAY, 0), '3')
        #FOULS
        self.assertEquals(match1.get_stat(MatchStats.FOULS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(MatchStats.FOULS, Match.COMPETITOR_AWAY, 0), '6')
        #POSSESSION
        self.assertEquals(match1.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_HOME, 0), '71.6')
        self.assertEquals(match1.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_AWAY, 0), '28.4')

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
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 2), '0')
        #RCARD
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match2.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match2.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match2.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_HOME, 0), '')
        self.assertEquals(match2.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '')
        #SHOTS
        self.assertEquals(match2.get_stat(MatchStats.SHOTS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match2.get_stat(MatchStats.SHOTS, Match.COMPETITOR_AWAY, 0), '5')
        #SHOTS_ON_TARGET
        self.assertEquals(match2.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match2.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '0')
        #CORNERS
        self.assertEquals(match2.get_stat(MatchStats.CORNERS, Match.COMPETITOR_HOME, 0), '7')
        self.assertEquals(match2.get_stat(MatchStats.CORNERS, Match.COMPETITOR_AWAY, 0), '0')
        #FOULS
        self.assertEquals(match2.get_stat(MatchStats.FOULS, Match.COMPETITOR_HOME, 0), '15')
        self.assertEquals(match2.get_stat(MatchStats.FOULS, Match.COMPETITOR_AWAY, 0), '10')
        #POSSESSION
        self.assertEquals(match2.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_HOME, 0), '55.1')
        self.assertEquals(match2.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_AWAY, 0), '44.9')

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
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 2), '2')
        #YCARD
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match3.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 2), '0')
        #RCARD
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match3.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match3.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '2')
        #YCARD_MINUTE
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '2')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match3.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match3.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_HOME, 0), '')
        self.assertEquals(match3.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '85,90')
        #SHOTS
        self.assertEquals(match3.get_stat(MatchStats.SHOTS, Match.COMPETITOR_HOME, 0), '10')
        self.assertEquals(match3.get_stat(MatchStats.SHOTS, Match.COMPETITOR_AWAY, 0), '16')
        #SHOTS_ON_TARGET
        self.assertEquals(match3.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '9')
        #CORNERS
        self.assertEquals(match3.get_stat(MatchStats.CORNERS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match3.get_stat(MatchStats.CORNERS, Match.COMPETITOR_AWAY, 0), '6')
        #FOULS
        self.assertEquals(match3.get_stat(MatchStats.FOULS, Match.COMPETITOR_HOME, 0), '10')
        self.assertEquals(match3.get_stat(MatchStats.FOULS, Match.COMPETITOR_AWAY, 0), '10')
        #POSSESSION
        self.assertEquals(match3.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_HOME, 0), '37.9')
        self.assertEquals(match3.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_AWAY, 0), '62.1')


        #Scottish Premiership
        scottish_premiership = League.objects.get(name= 'Scottish Premiership', load_source=self.handler)
        self.assertEquals(scottish_premiership.name, 'Scottish Premiership')
        self.assertEquals(scottish_premiership.country, Scotland)
        scottish_premiership_season = scottish_premiership.get_season(load_date)
        self.assertEquals(scottish_premiership_season.start_date, date(2018,8,4))
        self.assertEquals(scottish_premiership_season.end_date, date(2019,5,26))
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
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 2), '0')
        #YCARD
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 0), '2')
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 2), '2')
        self.assertEquals(match4.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 2), '1')
        #RCARD
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '1')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match4.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match4.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match4.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match4.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_HOME, 0), '9')
        self.assertEquals(match4.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '12,22')
        #SHOTS
        self.assertEquals(match4.get_stat(MatchStats.SHOTS, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match4.get_stat(MatchStats.SHOTS, Match.COMPETITOR_AWAY, 0), '6')
        #SHOTS_ON_TARGET
        self.assertEquals(match4.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match4.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '3')
        #CORNERS
        self.assertEquals(match4.get_stat(MatchStats.CORNERS, Match.COMPETITOR_HOME, 0), '4')
        self.assertEquals(match4.get_stat(MatchStats.CORNERS, Match.COMPETITOR_AWAY, 0), '2')
        #FOULS
        self.assertEquals(match4.get_stat(MatchStats.FOULS, Match.COMPETITOR_HOME, 0), '16')
        self.assertEquals(match4.get_stat(MatchStats.FOULS, Match.COMPETITOR_AWAY, 0), '7')
        #POSSESSION
        self.assertEquals(match4.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_HOME, 0), '31')
        self.assertEquals(match4.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_AWAY, 0), '69')


    #######################################################################
    @skip("Skip load html")
    def test_espn_process_site(self):
        Spain = Country.get_object('esp')
        self.assertIsNotNone(Spain)
        load_date = date(2019,2,9)

        self.handler.process(is_debug=True, start_date=load_date)
        # self.handler.process(is_debug=True, start_date=load_date, is_debug_path=False)

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
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 1), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 1), '2')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS, Match.COMPETITOR_AWAY, 2), '1')
        #YCARD
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 0), '6')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 0), '3')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 1), '2')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_HOME, 2), '4')
        self.assertEquals(match1.get_stat(MatchStats.YCARD, Match.COMPETITOR_AWAY, 2), '2')
        #RCARD
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 0), '1')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_HOME, 2), '1')
        self.assertEquals(match1.get_stat(MatchStats.RCARD, Match.COMPETITOR_AWAY, 2), '0')
        #PENALTY
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 0), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 0), '1')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 1), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 1), '1')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_HOME, 2), '0')
        self.assertEquals(match1.get_stat(MatchStats.PENALTY, Match.COMPETITOR_AWAY, 2), '0')
        #GOALS_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 30), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 45), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 75), '1')
        self.assertEquals(match1.get_stat(MatchStats.GOALS_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #YCARD_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 30), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 45), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 60), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 75), '3')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_HOME, 90), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '1')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '2')
        self.assertEquals(match1.get_stat(MatchStats.YCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #RCARD_MINUTE
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_HOME, 90), '1')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 15), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 30), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 45), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 60), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 75), '0')
        self.assertEquals(match1.get_stat(MatchStats.RCARD_MINUTE, Match.COMPETITOR_AWAY, 90), '0')
        #GOAL_TIME
        self.assertEquals(match1.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_HOME, 0), '25')
        self.assertEquals(match1.get_stat(MatchStats.GOAL_TIME, Match.COMPETITOR_AWAY, 0), '16,42,74')
        #SHOTS
        self.assertEquals(match1.get_stat(MatchStats.SHOTS, Match.COMPETITOR_HOME, 0), '11')
        self.assertEquals(match1.get_stat(MatchStats.SHOTS, Match.COMPETITOR_AWAY, 0), '11')
        #SHOTS_ON_TARGET
        self.assertEquals(match1.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_HOME, 0), '2')
        self.assertEquals(match1.get_stat(MatchStats.SHOTS_ON_TARGET, Match.COMPETITOR_AWAY, 0), '4')
        #CORNERS
        self.assertEquals(match1.get_stat(MatchStats.CORNERS, Match.COMPETITOR_HOME, 0), '3')
        self.assertEquals(match1.get_stat(MatchStats.CORNERS, Match.COMPETITOR_AWAY, 0), '4')
        #FOULS
        self.assertEquals(match1.get_stat(MatchStats.FOULS, Match.COMPETITOR_HOME, 0), '21')
        self.assertEquals(match1.get_stat(MatchStats.FOULS, Match.COMPETITOR_AWAY, 0), '16')
        #POSSESSION
        self.assertEquals(match1.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_HOME, 0), '34.2')
        self.assertEquals(match1.get_stat(MatchStats.POSSESSION, Match.COMPETITOR_AWAY, 0), '65.8')


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