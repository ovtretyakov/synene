from datetime import date
from decimal import Decimal

from django.test import TestCase

from project.football.models import FootballSource, FootballLeague, FootballTeam
from project.core.models import Country, TeamType, Match, Season, Sport, MatchStats
from ..models import (ValueType, Odd, BetType,
                      HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague, TeamSkill,
                      ForecastHandler, Predictor, ForecastSet, Forecast,
                      PredictorStandardPoisson, 
                      )



#######################################################################################
######  xGTest
#######################################################################################
class xGTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
        cls.load_source.is_betting=1
        cls.load_source.save()
        cls.russia = Country.objects.get(slug='rus')
        cls.country = cls.russia
        cls.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
        cls.league = FootballLeague.get_or_create(
                                                name='league', 
                                                load_source=cls.load_source
                                                )
        cls.team1 = FootballTeam.get_or_create(
                                                name='team1', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team2 = FootballTeam.get_or_create(
                                                name='team2', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team3 = FootballTeam.get_or_create(
                                                name='team3', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team4 = FootballTeam.get_or_create(
                                                name='team4', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team5 = FootballTeam.get_or_create(
                                                name='team5', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.team6 = FootballTeam.get_or_create(
                                                name='team6', 
                                                team_type=cls.team_type, country=cls.country, load_source=cls.load_source
                                                )
        cls.season1 = Season.objects.create(
                                            name='2017/2018',
                                            league=cls.league, start_date=date(2017, 8, 1), end_date=date(2018, 6, 10),
                                            load_source=cls.load_source
                                            )
        cls.season2 = Season.objects.create(
                                            name='2018/2019',
                                            league=cls.league, start_date=date(2018, 8, 1), end_date=date(2019, 6, 10),
                                            load_source=cls.load_source
                                            )
        cls.season3 = Season.objects.create(
                                            name='2019/2020',
                                            league=cls.league, start_date=date(2019, 8, 1), end_date=date(2020, 6, 10),
                                            load_source=cls.load_source
                                            )


        # Harvest params
        cls.harvest_handler = HarvestHandler.objects.create(
                                            slug = "test-xg", name = "xG Handler", handler = "xGHandler"
                                            )
        cls.harvest = Harvest.objects.create(
                                            slug = "test-hg-0",  name = "Calculate match xG",
                                            sport = Sport.objects.get(slug=Sport.FOOTBALL), 
                                            harvest_handler = cls.harvest_handler,
                                            value_type = ValueType.objects.get(slug=ValueType.MAIN),
                                            period =0, status = 'a'
                                            )
        HarvestConfig.objects.create(harvest = cls.harvest, code = "smooth-interval", value = "5")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "deviation-smooth-interval", value = "7")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "zero-value", value = "0.01")
        HarvestConfig.objects.create(harvest = cls.harvest, code = "deviation-zero-value", value = "0.5")
 
        cls.harvest_group = HarvestGroup.objects.create(
                                            slug = "test-hg-0-league", name = "Harvest League",
                                            harvest = cls.harvest, country = cls.country,
                                            status = 'a', harvest_date = date(2021, 1, 1)
                                            )

        HarvestLeague.objects.create(harvest_group = cls.harvest_group, league = cls.league)


        # Matches
        #match1
        cls.match1 = Match.objects.create(league=cls.league, team_h=cls.team1, team_a=cls.team5, 
                                           match_date=date(2018,3,1), season=cls.season1,
                                           score = "1:0(0:0,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=1)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=0)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=1.44)
        MatchStats.objects.create(match=cls.match1, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=0.64)
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team1, event_date =cls.match1.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match1, match_cnt = 1, param="h",
                                 lvalue1=0.1823, lvalue2=-0.2231, lvalue3=-0.1863, lvalue4=-0.1278, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.2, value2=0.8, value3=0.83, value4=0.88,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team5, event_date =cls.match1.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match1, match_cnt = 1, param="h",
                                 lvalue1=-0.2231, lvalue2=0.1823, lvalue3=-0.1278, lvalue4=-0.1863, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.8, value2=1.2, value3=0.88, value4=0.83,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.73, value10=0.96
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team1, event_date =cls.match1.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match1, match_cnt = 1, param="a",
                                 lvalue1=0.1823, lvalue2=-0.2231, lvalue3=-0.1863, lvalue4=-0.1278, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.2, value2=0.8, value3=0.83, value4=0.88,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team5, event_date =cls.match1.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match1, match_cnt = 1, param="a",
                                 lvalue1=-0.2231, lvalue2=0.1823, lvalue3=-0.1278, lvalue4=-0.1863, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.8, value2=1.2, value3=0.88, value4=0.83,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.73, value10=0.96
                                 )
        #match2
        cls.match2 = Match.objects.create(league=cls.league, team_h=cls.team1, team_a=cls.team2, 
                                           match_date=date(2019,3,1), season=cls.season2,
                                           score = "2:1(1:1,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=2)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=1)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=1.7)
        MatchStats.objects.create(match=cls.match2, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=0.8)
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team1, event_date =cls.match2.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match2, match_cnt = 2, param="h",
                                 lvalue1=0.4, lvalue2=-0.1, lvalue3=-0.5, lvalue4=-0.1, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.5, value2=0.9, value3=0.9, value4=0.8,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team2, event_date =cls.match2.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match2, match_cnt = 1, param="h",
                                 lvalue1=-0.2, lvalue2=0.18, lvalue3=-0.12, lvalue4=-0.18, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.9, value2=1.4, value3=1.1, value4=0.8,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.7, value10=0.9
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team1, event_date =cls.match2.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match2, match_cnt = 2, param="a",
                                 lvalue1=0.4, lvalue2=-0.1, lvalue3=-0.5, lvalue4=-0.1, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.5, value2=0.9, value3=0.9, value4=0.8,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team2, event_date =cls.match2.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match2, match_cnt = 1, param="a",
                                 lvalue1=-0.2, lvalue2=0.18, lvalue3=-0.12, lvalue4=-0.18, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.9, value2=1.4, value3=1.1, value4=0.8,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.7, value10=0.9
                                 )
        #match3
        cls.match3 = Match.objects.create(league=cls.league, team_h=cls.team3, team_a=cls.team4, 
                                           match_date=date(2019,3,1), season=cls.season2,
                                           score = "0:3(0:2,0:1)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match3, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=0)
        MatchStats.objects.create(match=cls.match3, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=3)
        MatchStats.objects.create(match=cls.match3, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=0.3)
        MatchStats.objects.create(match=cls.match3, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=3.2)
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team3, event_date =cls.match3.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match3, match_cnt = 1, param="h",
                                 lvalue1=-0.2, lvalue2=0.41, lvalue3=-0.1, lvalue4=-0.01, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.4, value2=1.5, value3=0.7, value4=0.6,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.6, value10=1.5
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team4, event_date =cls.match3.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match3, match_cnt = 1, param="h",
                                 lvalue1=0.8, lvalue2=-0.2, lvalue3=-0.1, lvalue4=0.1, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=2.5, value2=0.5, value3=0.9, value4=1.2,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=2.2, value10=1.0
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team3, event_date =cls.match3.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match3, match_cnt = 1, param="a",
                                 lvalue1=-0.2, lvalue2=0.41, lvalue3=-0.1, lvalue4=-0.01, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.4, value2=1.5, value3=0.7, value4=0.6,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.6, value10=1.5
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team4, event_date =cls.match3.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match3, match_cnt = 1, param="a",
                                 lvalue1=0.8, lvalue2=-0.2, lvalue3=-0.1, lvalue4=0.1, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=2.5, value2=0.5, value3=0.9, value4=1.2,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=2.2, value10=1.0
                                 )
        #match4
        cls.match4 = Match.objects.create(league=cls.league, team_h=cls.team1, team_a=cls.team5, 
                                           match_date=date(2020,3,1), season=cls.season3,
                                           score = "2:0(1:0,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match4, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=2)
        MatchStats.objects.create(match=cls.match4, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=0)
        MatchStats.objects.create(match=cls.match4, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=1.8)
        MatchStats.objects.create(match=cls.match4, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=1.1)
        #match5
        cls.match5 = Match.objects.create(league=cls.league, team_h=cls.team2, team_a=cls.team6, 
                                           match_date=date(2020,3,1), season=cls.season3,
                                           score = "2:2(1:0,1:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match5, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=2)
        MatchStats.objects.create(match=cls.match5, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=2)
        MatchStats.objects.create(match=cls.match5, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=2.2)
        MatchStats.objects.create(match=cls.match5, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=1.2)
        #match6
        cls.match6 = Match.objects.create(league=cls.league, team_h=cls.team2, team_a=cls.team1, 
                                           match_date=date(2020,3,5), season=cls.season3,
                                           score = "0:0(0:0,0:0)", status = Match.FINISHED,
                                           load_source=cls.load_source)
        MatchStats.objects.create(match=cls.match6, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=0)
        MatchStats.objects.create(match=cls.match6, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=0)
        MatchStats.objects.create(match=cls.match6, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=1.5)
        MatchStats.objects.create(match=cls.match6, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=0.2)

        # Forecasting
        cls.forecast_handler = ForecastHandler.objects.create(
                                            slug = "test-xg-forecast-standard", name = "xG Forecasting", handler = "PredictorStandardPoisson"
                                            )
        cls.forecast_set = ForecastSet.objects.create(
                                            slug = "test-main",
                                            name = "Main Forecasting",
                                            status = "p",
                                            keep_only_best = False,
                                            only_finished = False,
                                            start_date = date(2020,1,1),
                                            )
        cls.predictor = Predictor.objects.create(
                                            slug = "test-hg-standard",
                                            name = "xG Standard",
                                            forecast_handler = cls.forecast_handler,
                                            harvest = cls.harvest,
                                            priority = 10,
                                            status = 'a'
                                            )


    #######################################################################
    def test_get_team_skill(self):
        # self.harvest.harvesting()

        team_skill = TeamSkill.get_team_skill(self.harvest, self.team1, self.match4.match_date, self.match4, param="h")
        self.assertEquals(team_skill.event_date, self.match2.match_date)
        self.assertEquals(team_skill.match_cnt, 2)
        self.assertEquals(team_skill.lvalue1, Decimal('0.4'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.1'))

        team_skill = TeamSkill.get_team_skill(self.harvest, self.team1, date(2019,3,2), self.match2, param="h")
        self.assertEquals(team_skill.event_date, self.match2.match_date)
        self.assertEquals(team_skill.match_cnt, 2)
        self.assertEquals(team_skill.lvalue1, Decimal('0.4'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.1'))

        team_skill = TeamSkill.get_team_skill(self.harvest, self.team1, self.match2.match_date, self.match2, param="h")
        self.assertEquals(team_skill.event_date, self.match1.match_date)
        self.assertEquals(team_skill.match_cnt, 1)
        self.assertEquals(team_skill.lvalue1, Decimal('0.1823'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.2231'))

        team_skill = TeamSkill.get_team_skill(self.harvest, self.team1, self.match1.match_date, self.match1, param="h")
        self.assertEquals(team_skill.event_date, self.match1.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('0'))
        self.assertEquals(team_skill.lvalue2, Decimal('0'))

        team_skill = TeamSkill.get_team_skill(self.harvest, self.team5, self.match4.match_date, self.match4, param="a")
        self.assertEquals(team_skill.event_date, self.match4.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('-0.2'))
        self.assertEquals(team_skill.lvalue2, Decimal('0.295'))
        self.assertEquals(team_skill.lvalue3, Decimal('-0.11'))
        self.assertEquals(team_skill.lvalue4, Decimal('-0.095'))


        team_skill = TeamSkill.get_team_skill(self.harvest, self.team6, self.match5.match_date, self.match5, param="h")
        self.assertEquals(team_skill.event_date, self.match5.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('-0.2'))
        self.assertEquals(team_skill.lvalue2, Decimal('0.295'))
        self.assertEquals(team_skill.lvalue3, Decimal('-0.11'))
        self.assertEquals(team_skill.lvalue4, Decimal('-0.095'))

    #######################################################################
    def test_harvest_group(self):
        self.harvest.do_harvest(self.match4.match_date)

        self.harvest_group.refresh_from_db()
        self.assertEquals(self.harvest_group.harvest_date, self.match6.match_date)

        team_skill_1 = TeamSkill.objects.get(harvest=self.harvest, team=self.team1, event_date=self.match4.match_date)
        self.assertEquals(team_skill_1.match_cnt, 3)
        self.assertEquals(team_skill_1.lvalue1, Decimal("0.38213"))
        self.assertEquals(team_skill_1.lvalue2, Decimal("-0.03411"))
        self.assertEquals(team_skill_1.lvalue3, Decimal("-0.41245"))
        self.assertEquals(team_skill_1.lvalue4, Decimal("-0.17231"))
        self.assertEquals(team_skill_1.value1, Decimal("1.46540"))
        self.assertEquals(team_skill_1.value2, Decimal("0.96646"))
        self.assertEquals(team_skill_1.value3, Decimal("0.66202"))
        self.assertEquals(team_skill_1.value4, Decimal("0.84172"))
        self.assertEquals(team_skill_1.value9, Decimal("0.97013"))
        self.assertEquals(team_skill_1.value10, Decimal("0.81349"))

    #######################################################################
    def test_forecasting(self):
        TeamSkill.objects.filter(harvest=self.harvest).update(match_cnt = 10)

        odd_w = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='w', odd_value=2)
        odd_d = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='d', odd_value=3)
        odd_l = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='l', odd_value=4)
        odd_wd = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='wd', odd_value=1.5)
        odd_wl = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='wl', odd_value=1.6)
        odd_dl = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='ld', odd_value=1.7)
        odd_w_1 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=1, yes='Y', team='', param='w', odd_value=2)
        odd_half1_fill = Odd.create(match=self.match6,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1/2', odd_value=3.1)
        odd_win_to_nil = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='h', param='', odd_value=3.1)
        odd_correct_score = Odd.create(match=self.match6,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1:1', odd_value=6.1)
        odd_even_odd = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='even', odd_value=2.1)
        odd_over_15 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1.5', odd_value=1.8)
        odd_over_2 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='2.0', odd_value=1.8)
        odd_over_225 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='2.25', odd_value=1.8)
        odd_under_25 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='2.5', odd_value=1.8)
        odd_total_12 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1,2', odd_value=3.1)
        odd_handicap_0 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='h', param='0', odd_value=2)
        odd_iboth_over_05 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='0.5', odd_value=3.1)
        odd_iboth_under_05 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='0.5', odd_value=3.5)
        odd_only_over_05 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.ITOTAL_ONLY_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='h', param='0.5', odd_value=4)
        odd_only_under_05 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.ITOTAL_ONLY_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='0.5', odd_value=4)
        odd_least_over_05 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.ITOTAL_AT_LEAST_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='0.5', odd_value=2)
        odd_margin_01 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.MARGIN, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='h', param='0,1', odd_value=2)
        odd_win_over_15 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.W_AND_TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='1.5', odd_value=3)
        odd_win_under_25 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.W_AND_TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='2.5', odd_value=3)
        odd_wd_over_15 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WD_AND_TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='1.5', odd_value=3)
        odd_wd_under_25 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WD_AND_TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='2.5', odd_value=3)
        odd_bothscore_over_25 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.BOTH_TO_SCORE_AND_TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='2.5', odd_value=3)
        odd_bothscore_under_35 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.BOTH_TO_SCORE_AND_TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='3.5', odd_value=3)
        odd_not_bothscore_over_15 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3)
        odd_not_bothscore_under_15 = Odd.create(match=self.match6,
                            bet_type_slug=BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3)
        odd_bothscore_d = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WDL_AND_BOTH_TEAMS_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='', param='d', odd_value=4)
        odd_win_nobet = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WIN_NO_BET, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='d', odd_value=2)
        odd_win_itotal_over = Odd.create(match=self.match6,
                            bet_type_slug=BetType.W_AND_ITOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='1.5', odd_value=2)
        odd_wd_itotal_under = Odd.create(match=self.match6,
                            bet_type_slug=BetType.WD_AND_ITOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='1.5', odd_value=2)
        odd_win_total = Odd.create(match=self.match6,
                            bet_type_slug=BetType.W_AND_TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source, bookie=self.load_source, 
                            period=0, yes='Y', team='a', param='1,2', odd_value=2)



        predictor = PredictorStandardPoisson.objects.get(slug=self.predictor.slug)
        predictor.forecasting(self.forecast_set)

        forecast_w = Forecast.objects.filter(odd=odd_w).first()
        self.assertEquals(forecast_w.success_chance, Decimal("0.205"))
        self.assertEquals(forecast_w.lose_chance, Decimal("0.795"))
        self.assertEquals(forecast_w.result_value, Decimal("0.410"))
        self.assertEquals(forecast_w.kelly, Decimal("0"))

        forecast_d = Forecast.objects.filter(odd=odd_d).first()
        self.assertEquals(forecast_d.success_chance, Decimal("0.377"))
        self.assertEquals(forecast_d.lose_chance, Decimal("0.623"))
        self.assertEquals(forecast_d.result_value, Decimal("1.132"))
        self.assertEquals(forecast_d.kelly, Decimal("0.066"))

        forecast_l = Forecast.objects.filter(odd=odd_l).first()
        self.assertEquals(forecast_l.success_chance, Decimal("0.417"))
        self.assertEquals(forecast_l.lose_chance, Decimal("0.583"))
        self.assertEquals(forecast_l.result_value, Decimal("1.669"))
        self.assertEquals(forecast_l.kelly, Decimal("0.223"))

        forecast_wd = Forecast.objects.filter(odd=odd_wd).first()
        self.assertEquals(forecast_wd.success_chance, Decimal("0.583"))
        self.assertEquals(forecast_wd.lose_chance, Decimal("0.417"))
        self.assertEquals(forecast_wd.result_value, Decimal("0.874"))
        self.assertEquals(forecast_wd.kelly, Decimal("0"))

        forecast_wl = Forecast.objects.filter(odd=odd_wl).first()
        self.assertEquals(forecast_wl.success_chance, Decimal("0.623"))
        self.assertEquals(forecast_wl.lose_chance, Decimal("0.377"))
        self.assertEquals(forecast_wl.result_value, Decimal("0.996"))
        self.assertEquals(forecast_wl.kelly, Decimal("0"))

        forecast_dl = Forecast.objects.filter(odd=odd_dl).first()
        self.assertEquals(forecast_dl.success_chance, Decimal("0.795"))
        self.assertEquals(forecast_dl.lose_chance, Decimal("0.205"))
        self.assertEquals(forecast_dl.result_value, Decimal("1.351"))
        self.assertEquals(forecast_dl.kelly, Decimal("0.502"))

        forecast_w_1 = Forecast.objects.filter(odd=odd_w_1).first()
        self.assertEquals(forecast_w_1, None)

        forecast_half1_fill = Forecast.objects.filter(odd=odd_half1_fill).first()
        self.assertEquals(forecast_half1_fill, None)

        forecast_win_to_nil = Forecast.objects.filter(odd=odd_win_to_nil).first()
        self.assertEquals(forecast_win_to_nil.success_chance, Decimal("0.169"))
        self.assertEquals(forecast_win_to_nil.lose_chance, Decimal("0.831"))
        self.assertEquals(forecast_win_to_nil.result_value, Decimal("0.523"))
        self.assertEquals(forecast_win_to_nil.kelly, Decimal("0"))

        forecast_correct_score = Forecast.objects.filter(odd=odd_correct_score).first()
        self.assertEquals(forecast_correct_score.success_chance, Decimal("0.112"))
        self.assertEquals(forecast_correct_score.lose_chance, Decimal("0.888"))
        self.assertEquals(forecast_correct_score.result_value, Decimal("0.681"))
        self.assertEquals(forecast_correct_score.kelly, Decimal("0"))

        forecast_even_odd = Forecast.objects.filter(odd=odd_even_odd).first()
        self.assertEquals(forecast_even_odd.success_chance, Decimal("0.532"))
        self.assertEquals(forecast_even_odd.lose_chance, Decimal("0.468"))
        self.assertEquals(forecast_even_odd.result_value, Decimal("1.117"))
        self.assertEquals(forecast_even_odd.kelly, Decimal("0.106"))

        forecast_over_15 = Forecast.objects.filter(odd=odd_over_15).first()
        self.assertEquals(forecast_over_15.success_chance, Decimal("0.399"))
        self.assertEquals(forecast_over_15.lose_chance, Decimal("0.600"))
        self.assertEquals(forecast_over_15.result_value, Decimal("0.719"))
        self.assertEquals(forecast_over_15.kelly, Decimal("0"))

        forecast_over_2 = Forecast.objects.filter(odd=odd_over_2).first()
        self.assertEquals(forecast_over_2.success_chance, Decimal("0.399"))
        self.assertEquals(forecast_over_2.lose_chance, Decimal("0.600"))
        self.assertEquals(forecast_over_2.result_value, Decimal("0.528"))
        self.assertEquals(forecast_over_2.kelly, Decimal("0"))

        forecast_over_225 = Forecast.objects.filter(odd=odd_over_225).first()
        self.assertEquals(forecast_over_225.success_chance, Decimal("0.160"))
        self.assertEquals(forecast_over_225.lose_chance, Decimal("0.840"))
        self.assertEquals(forecast_over_225.result_value, Decimal("0.408"))
        self.assertEquals(forecast_over_225.kelly, Decimal("0"))

        forecast_under_25 = Forecast.objects.filter(odd=odd_under_25).first()
        self.assertEquals(forecast_under_25.success_chance, Decimal("0.840"))
        self.assertEquals(forecast_under_25.lose_chance, Decimal("0.160"))
        self.assertEquals(forecast_under_25.result_value, Decimal("1.511"))
        self.assertEquals(forecast_under_25.kelly, Decimal("0.639"))

        forecast_total_12 = Forecast.objects.filter(odd=odd_total_12).first()
        self.assertEquals(forecast_total_12.success_chance, Decimal("0.587"))
        self.assertEquals(forecast_total_12.lose_chance, Decimal("0.413"))
        self.assertEquals(forecast_total_12.result_value, Decimal("1.819"))
        self.assertEquals(forecast_total_12.kelly, Decimal("0.39"))

        forecast_handicap_0 = Forecast.objects.filter(odd=odd_handicap_0).first()
        self.assertEquals(forecast_handicap_0.success_chance, Decimal("0.583"))
        self.assertEquals(forecast_handicap_0.lose_chance, Decimal("0.417"))
        self.assertEquals(forecast_handicap_0.result_value, Decimal("0.788"))
        self.assertEquals(forecast_handicap_0.kelly, Decimal("0"))

        forecast_iboth_over_05 = Forecast.objects.filter(odd=odd_iboth_over_05).first()
        self.assertEquals(forecast_iboth_over_05.success_chance, Decimal("0.231"))
        self.assertEquals(forecast_iboth_over_05.lose_chance, Decimal("0.769"))
        self.assertEquals(forecast_iboth_over_05.result_value, Decimal("0.718"))
        self.assertEquals(forecast_iboth_over_05.kelly, Decimal("0"))

        forecast_iboth_under_05 = Forecast.objects.filter(odd=odd_iboth_under_05).first()
        self.assertEquals(forecast_iboth_under_05.success_chance, Decimal("0.253"))
        self.assertEquals(forecast_iboth_under_05.lose_chance, Decimal("0.747"))
        self.assertEquals(forecast_iboth_under_05.result_value, Decimal("0.885"))
        self.assertEquals(forecast_iboth_under_05.kelly, Decimal("0"))

        forecast_only_over_05 = Forecast.objects.filter(odd=odd_only_over_05).first()
        self.assertEquals(forecast_only_over_05.success_chance, Decimal("0.169"))
        self.assertEquals(forecast_only_over_05.lose_chance, Decimal("0.831"))
        self.assertEquals(forecast_only_over_05.result_value, Decimal("0.675"))
        self.assertEquals(forecast_only_over_05.kelly, Decimal("0"))

        forecast_only_under_05 = Forecast.objects.filter(odd=odd_only_under_05).first()
        self.assertEquals(forecast_only_under_05.success_chance, Decimal("0.516"))
        self.assertEquals(forecast_only_under_05.lose_chance, Decimal("0.484"))
        self.assertEquals(forecast_only_under_05.result_value, Decimal("2.063"))
        self.assertEquals(forecast_only_under_05.kelly, Decimal("0.354"))

        forecast_least_over_05 = Forecast.objects.filter(odd=odd_least_over_05).first()
        self.assertEquals(forecast_least_over_05.success_chance, Decimal("0.747"))
        self.assertEquals(forecast_least_over_05.lose_chance, Decimal("0.253"))
        self.assertEquals(forecast_least_over_05.result_value, Decimal("1.494"))
        self.assertEquals(forecast_least_over_05.kelly, Decimal("0.494"))

        forecast_margin_01 = Forecast.objects.filter(odd=odd_margin_01).first()
        self.assertEquals(forecast_margin_01.success_chance, Decimal("0.537"))
        self.assertEquals(forecast_margin_01.lose_chance, Decimal("0.463"))
        self.assertEquals(forecast_margin_01.result_value, Decimal("1.075"))
        self.assertEquals(forecast_margin_01.kelly, Decimal("0.075"))

        forecast_win_over_15 = Forecast.objects.filter(odd=odd_win_over_15).first()
        self.assertEquals(forecast_win_over_15.success_chance, Decimal("0.199"))
        self.assertEquals(forecast_win_over_15.lose_chance, Decimal("0.801"))
        self.assertEquals(forecast_win_over_15.result_value, Decimal("0.597"))
        self.assertEquals(forecast_win_over_15.kelly, Decimal("0"))

        forecast_win_under_25 = Forecast.objects.filter(odd=odd_win_under_25).first()
        self.assertEquals(forecast_win_under_25.success_chance, Decimal("0.313"))
        self.assertEquals(forecast_win_under_25.lose_chance, Decimal("0.687"))
        self.assertEquals(forecast_win_under_25.result_value, Decimal("0.938"))
        self.assertEquals(forecast_win_under_25.kelly, Decimal("0"))

        forecast_wd_over_15 = Forecast.objects.filter(odd=odd_wd_over_15).first()
        self.assertEquals(forecast_wd_over_15.success_chance, Decimal("0.323"))
        self.assertEquals(forecast_wd_over_15.lose_chance, Decimal("0.676"))
        self.assertEquals(forecast_wd_over_15.result_value, Decimal("0.970"))
        self.assertEquals(forecast_wd_over_15.kelly, Decimal("0"))

        forecast_wd_under_25 = Forecast.objects.filter(odd=odd_wd_under_25).first()
        self.assertEquals(forecast_wd_under_25.success_chance, Decimal("0.677"))
        self.assertEquals(forecast_wd_under_25.lose_chance, Decimal("0.323"))
        self.assertEquals(forecast_wd_under_25.result_value, Decimal("2.032"))
        self.assertEquals(forecast_wd_under_25.kelly, Decimal("0.516"))

        forecast_bothscore_over_25 = Forecast.objects.filter(odd=odd_bothscore_over_25).first()
        self.assertEquals(forecast_bothscore_over_25.success_chance, Decimal("0.120"))
        self.assertEquals(forecast_bothscore_over_25.lose_chance, Decimal("0.88"))
        self.assertEquals(forecast_bothscore_over_25.result_value, Decimal("0.359"))
        self.assertEquals(forecast_bothscore_over_25.kelly, Decimal("0"))

        forecast_bothscore_under_35 = Forecast.objects.filter(odd=odd_bothscore_under_35).first()
        self.assertEquals(forecast_bothscore_under_35.success_chance, Decimal("0.188"))
        self.assertEquals(forecast_bothscore_under_35.lose_chance, Decimal("0.812"))
        self.assertEquals(forecast_bothscore_under_35.result_value, Decimal("0.565"))
        self.assertEquals(forecast_bothscore_under_35.kelly, Decimal("0"))

        forecast_not_bothscore_over_15 = Forecast.objects.filter(odd=odd_not_bothscore_over_15).first()
        self.assertEquals(forecast_not_bothscore_over_15.success_chance, Decimal("0.168"))
        self.assertEquals(forecast_not_bothscore_over_15.lose_chance, Decimal("0.832"))
        self.assertEquals(forecast_not_bothscore_over_15.result_value, Decimal("0.504"))
        self.assertEquals(forecast_not_bothscore_over_15.kelly, Decimal("0"))

        forecast_not_bothscore_under_15 = Forecast.objects.filter(odd=odd_not_bothscore_under_15).first()
        self.assertEquals(forecast_not_bothscore_under_15.success_chance, Decimal("0.6"))
        self.assertEquals(forecast_not_bothscore_under_15.lose_chance, Decimal("0.399"))
        self.assertEquals(forecast_not_bothscore_under_15.result_value, Decimal("1.801"))
        self.assertEquals(forecast_not_bothscore_under_15.kelly, Decimal("0.401"))

        forecast_bothscore_d = Forecast.objects.filter(odd=odd_bothscore_d).first()
        self.assertEquals(forecast_bothscore_d.success_chance, Decimal("0.125"))
        self.assertEquals(forecast_bothscore_d.lose_chance, Decimal("0.875"))
        self.assertEquals(forecast_bothscore_d.result_value, Decimal("0.498"))
        self.assertEquals(forecast_bothscore_d.kelly, Decimal("0"))

        forecast_win_nobet = Forecast.objects.filter(odd=odd_win_nobet).first()
        self.assertEquals(forecast_win_nobet.success_chance, Decimal("0.795"))
        self.assertEquals(forecast_win_nobet.lose_chance, Decimal("0.205"))
        self.assertEquals(forecast_win_nobet.result_value, Decimal("1.172"))
        self.assertEquals(forecast_win_nobet.kelly, Decimal("0.172"))

        forecast_win_itotal_over = Forecast.objects.filter(odd=odd_win_itotal_over).first()
        self.assertEquals(forecast_win_itotal_over.success_chance, Decimal("0.199"))
        self.assertEquals(forecast_win_itotal_over.lose_chance, Decimal("0.801"))
        self.assertEquals(forecast_win_itotal_over.result_value, Decimal("0.398"))
        self.assertEquals(forecast_win_itotal_over.kelly, Decimal("0"))

        forecast_wd_itotal_under = Forecast.objects.filter(odd=odd_wd_itotal_under).first()
        self.assertEquals(forecast_wd_itotal_under.success_chance, Decimal("0.583"))
        self.assertEquals(forecast_wd_itotal_under.lose_chance, Decimal("0.417"))
        self.assertEquals(forecast_wd_itotal_under.result_value, Decimal("1.166"))
        self.assertEquals(forecast_wd_itotal_under.kelly, Decimal("0.166"))

        forecast_win_total = Forecast.objects.filter(odd=odd_win_total).first()
        self.assertEquals(forecast_win_total.success_chance, Decimal("0.313"))
        self.assertEquals(forecast_win_total.lose_chance, Decimal("0.687"))
        self.assertEquals(forecast_win_total.result_value, Decimal("0.626"))
        self.assertEquals(forecast_win_total.kelly, Decimal("0"))
