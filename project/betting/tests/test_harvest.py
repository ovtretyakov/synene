from datetime import date
from decimal import Decimal

from django.test import TestCase

from project.football.models import FootballSource, FootballLeague, FootballTeam
from project.core.models import Country, TeamType, Match, Season, Sport, MatchStats
from ..models import (ValueType,
                      HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague, TeamSkill
                      )



#######################################################################################
######  xGTest
#######################################################################################
class xGTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
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
                                 match = cls.match1, match_cnt = 1,
                                 lvalue1=0.1823, lvalue2=-0.2231, lvalue3=-0.1863, lvalue4=-0.1278, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.2, value2=0.8, value3=0.83, value4=0.88,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team5, event_date =cls.match1.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match1, match_cnt = 1,
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
                                 match = cls.match2, match_cnt = 2,
                                 lvalue1=0.4, lvalue2=-0.1, lvalue3=-0.5, lvalue4=-0.1, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=1.5, value2=0.9, value3=0.9, value4=0.8,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.96, value10=0.73
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team2, event_date =cls.match2.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match2, match_cnt = 1,
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
                                 match = cls.match3, match_cnt = 1,
                                 lvalue1=-0.2, lvalue2=0.41, lvalue3=-0.1, lvalue4=-0.01, 
                                 lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
                                 value1=0.4, value2=1.5, value3=0.7, value4=0.6,
                                 value5=0, value6=0, value7=0, value8=0, 
                                 value9=0.6, value10=1.5
                                 )
        TeamSkill.objects.create(harvest = cls.harvest, team = cls.team4, event_date =cls.match3.match_date,
                                 harvest_group = cls.harvest_group,
                                 match = cls.match3, match_cnt = 1,
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


    #######################################################################
    def test_get_team_skill(self):
        # self.harvest.harvesting()

        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team1, self.match4.match_date, self.match4)
        self.assertEquals(team_skill.event_date, self.match2.match_date)
        self.assertEquals(team_skill.match_cnt, 2)
        self.assertEquals(team_skill.lvalue1, Decimal('0.4'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.1'))

        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team1, date(2019,3,2), self.match2)
        self.assertEquals(team_skill.event_date, self.match2.match_date)
        self.assertEquals(team_skill.match_cnt, 2)
        self.assertEquals(team_skill.lvalue1, Decimal('0.4'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.1'))

        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team1, self.match2.match_date, self.match2)
        self.assertEquals(team_skill.event_date, self.match1.match_date)
        self.assertEquals(team_skill.match_cnt, 1)
        self.assertEquals(team_skill.lvalue1, Decimal('0.1823'))
        self.assertEquals(team_skill.lvalue2, Decimal('-0.2231'))

        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team1, self.match1.match_date, self.match1)
        self.assertEquals(team_skill.event_date, self.match1.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('0'))
        self.assertEquals(team_skill.lvalue2, Decimal('0'))

        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team5, self.match4.match_date, self.match4)
        self.assertEquals(team_skill.event_date, self.match4.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('-0.2'))
        self.assertEquals(team_skill.lvalue2, Decimal('0.295'))
        self.assertEquals(team_skill.lvalue3, Decimal('-0.11'))
        self.assertEquals(team_skill.lvalue4, Decimal('-0.095'))


        team_skill = TeamSkill.getTeamSkill(self.harvest, self.team6, self.match5.match_date, self.match5)
        self.assertEquals(team_skill.event_date, self.match5.match_date)
        self.assertEquals(team_skill.match_cnt, 0)
        self.assertEquals(team_skill.lvalue1, Decimal('-0.2'))
        self.assertEquals(team_skill.lvalue2, Decimal('0.295'))
        self.assertEquals(team_skill.lvalue3, Decimal('-0.11'))
        self.assertEquals(team_skill.lvalue4, Decimal('-0.095'))

    #######################################################################
    def test_get_team_skill(self):
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


        # a1 = 2/(N+1) = 0,33333333333333
        # a2 = 2/(N+1) = 0,125
        #    = a * P + (1-a) * EMA        

        # 0,4 + 0,295 = 0,695
        # ln(1.8) = 0,58778666490
        # delta = -0,05360666755
        # P = 0,34639333245
        # new =  

        # MatchStats.objects.create(match=cls.match4, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=2)
        # MatchStats.objects.create(match=cls.match4, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=0)
        # MatchStats.objects.create(match=cls.match4, stat_type=Match.XG, competitor=Match.COMPETITOR_HOME, period=0, value=1.8)
        # MatchStats.objects.create(match=cls.match4, stat_type=Match.XG, competitor=Match.COMPETITOR_AWAY, period=0, value=1.1)


        # TeamSkill.objects.create(harvest = cls.harvest, team = cls.team1, event_date =cls.match2.match_date,
        #                          harvest_group = cls.harvest_group,
        #                          match = cls.match2, match_cnt = 2,
        #                          lvalue1=0.4, lvalue2=-0.1, lvalue3=-0.5, lvalue4=-0.1, 
        #                          lvalue5=0, lvalue6=0, lvalue7=0, lvalue8=0, lvalue9=0, lvalue10=0, 
        #                          value1=1.5, value2=0.9, value3=0.9, value4=0.8,
        #                          value5=0, value6=0, value7=0, value8=0, 
        #                          value9=0.96, value10=0.73
        #                          )

        # team5 = 0