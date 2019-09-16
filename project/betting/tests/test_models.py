from datetime import date
from decimal import Decimal

from django.test import TestCase

from project.football.models import FootballSource,FootballLeague,FootballTeam
from project.core.models import Country,TeamType,Match,MatchStats
from ..models import Odd,BetType,ValueType


def prepare_data(obj):
    obj.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
    obj.bookie = obj.load_source
    obj.bookie.is_betting=1
    obj.bookie.save()
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.load_source_1, created = FootballSource.objects.get_or_create(
                                                slug = 'test_load_source_1', 
                                                defaults={'name':'test_load_source_1', 'reliability':1}
                                                )
    obj.load_source_2, created = FootballSource.objects.get_or_create(
                                                slug = 'test_load_source_2', 
                                                defaults={'name':'test_load_source_2', 'reliability':2}
                                                )
    obj.load_source_3, created = FootballSource.objects.get_or_create(
                                                slug = 'test_load_source_3', 
                                                defaults={'name':'test_load_source_3', 'reliability':3}
                                                )
    obj.league = FootballLeague.get_or_create(
                                            name='test_odd_model_league', 
                                            load_source=obj.load_source_1
                                            )
    obj.team1 = FootballTeam.get_or_create(
                                            name='test_odd_model_team 1', 
                                            team_type=obj.team_type, country=obj.country, load_source=obj.load_source_1
                                            )
    obj.team2 = FootballTeam.get_or_create(
                                            name='test_odd_model_team 2', 
                                            team_type=obj.team_type, country=obj.country, load_source=obj.load_source_1
                                            )
    ###### match1
    obj.match1 = Match.get_or_create(
                                    league=obj.league, 
                                    team_h=obj.team1, 
                                    team_a=obj.team2, 
                                    match_date=date(2016,8,2), 
                                    load_source=obj.load_source_2, 
                                    status=Match.FINISHED
                                    )
    #GOALS
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=2)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=2)
    #GOALS - periods
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=1, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=1, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=2, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=2, value=2)
    #GOALS - minutes
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=15, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=15, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=30, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=30, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=45, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=45, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=60, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=60, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=75, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=75, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=90, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=90, value=0)
    #GOAL_TIME
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOAL_TIME, competitor=Match.COMPETITOR_HOME, period=0, value='12,53')
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOAL_TIME, competitor=Match.COMPETITOR_AWAY, period=0, value='54,70')
    ###### match2
    obj.match2 = Match.get_or_create(
                                    league=obj.league, 
                                    team_h=obj.team1, 
                                    team_a=obj.team2, 
                                    match_date=date(2017,8,2), 
                                    load_source=obj.load_source_2, 
                                    status=Match.FINISHED
                                    )
    #GOALS
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=0, value=3)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=0, value=1)
    #GOALS - periods
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=1, value=1)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=1, value=0)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_HOME, period=2, value=2)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMPETITOR_AWAY, period=2, value=1)
    #GOAL_TIME
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOAL_TIME, competitor=Match.COMPETITOR_HOME, period=0, value='43,46,90')
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOAL_TIME, competitor=Match.COMPETITOR_AWAY, period=0, value='47')


#######################################################################################
######  Odd
#######################################################################################
class OddModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_odd_change_match(self):
        match2 = Match.objects.create(league=self.league, team_h=self.team1, team_a=self.team2, 
                              match_date=date(2016,10,13), 
                              load_source=self.load_source_2)
        odd11 = Odd.objects.create(match = self.match1,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 0,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 1.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_2, 
                                   )
        odd11_pk = odd11.pk
        odd12 = Odd.objects.create(match = self.match1,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 1,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 1.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_2, 
                                   )
        odd12_pk = odd12.pk
        odd21 = Odd.objects.create(match = match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 0,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 2.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_2, 
                                   )
        odd21_pk = odd21.pk
        odd22 = Odd.objects.create(match = match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 1,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 2.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_1, 
                                   )
        odd22_pk = odd22.pk
        odd23 = Odd.objects.create(match = match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 2,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 2.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_2, 
                                   )
        odd23_pk = odd23.pk
        # 1
        odd21.change_match(self.match1)
        odd11.refresh_from_db()
        self.assertEquals(odd11.odd_value, 1.5)
        with self.assertRaises(Odd.DoesNotExist):
            stat = Odd.objects.get(pk=odd21_pk)
        # 2
        odd22.change_match(self.match1)
        odd12.refresh_from_db()
        self.assertEquals(odd12.odd_value, 2.5)
        with self.assertRaises(Odd.DoesNotExist):
            stat = Odd.objects.get(pk=odd22_pk)
        # 3
        odd23.change_match(self.match1)
        odd23.refresh_from_db()
        self.assertEquals(odd23.match, self.match1)

    def test_odd_wdl_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='W', odd_value=1)
        odd1_pk = odd1.pk
        self.assertEquals(odd1.match, self.match1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.WDL))
        self.assertEquals(odd1.value_type, ValueType.objects.get(slug=ValueType.MAIN))
        self.assertEquals(odd1.load_source, self.load_source_2)
        self.assertEquals(odd1.bookie, self.bookie)
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, 'w')
        self.assertEquals(odd1.odd_value, 1)
        #update value
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='w', odd_value=1.5)
        odd2_pk = odd2.pk
        self.assertEquals(odd1_pk, odd2_pk)
        self.assertEquals(odd2.odd_value, 1.5)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Unknown value_type'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug='Wrong',
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Yes', team='', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Wrong', team='', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='h', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid bet value'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='w', odd_value=-1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='wrong', odd_value=1.5)


    #######################################################################
    def test_odd_wdl_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='d', odd_value=2)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='d', odd_value=2)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='w', odd_value=2)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='w', odd_value=2)
        #period 1 - win
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='', param='w', odd_value=2)
        #period 2 - loose
        odd6 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='l', odd_value=2)

        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 2)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 2)
        #period 1 - win
        odd5.calculate_result()
        self.assertEquals(odd5.status, Odd.FINISHED)
        self.assertEquals(odd5.result, Odd.SUCCESS)
        self.assertEquals(odd5.result_value, 2)
        #period 2 - loose
        odd6.calculate_result()
        self.assertEquals(odd6.status, Odd.FINISHED)
        self.assertEquals(odd6.result, Odd.SUCCESS)
        self.assertEquals(odd6.result_value, 2)

    #######################################################################
    def test_odd_wdl_minute_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Yes', team='', param='W', odd_value=1)
        odd1_pk = odd1.pk
        self.assertEquals(odd1.match, self.match1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.WDL_MINUTE))
        self.assertEquals(odd1.value_type, ValueType.objects.get(slug=ValueType.MAIN))
        self.assertEquals(odd1.load_source, self.load_source_2)
        self.assertEquals(odd1.bookie, self.bookie)
        self.assertEquals(odd1.period, 15)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, 'w')
        self.assertEquals(odd1.odd_value, 1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Yes', team='', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=30, yes='Wrong', team='', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=45, yes='Yes', team='h', param='w', odd_value=1.5)
        with self.assertRaisesRegex(ValueError, 'Invalid bet value'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=60, yes='Yes', team='', param='w', odd_value=-1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=75, yes='Yes', team='', param='wrong', odd_value=1.5)

    #######################################################################
    def test_odd_wdl_minute_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='', param='w', odd_value=2)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='N', team='', param='w', odd_value=2)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=30, yes='Y', team='', param='w', odd_value=2)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=30, yes='N', team='', param='w', odd_value=2)
        #draw
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=45, yes='Y', team='', param='d', odd_value=2)
        #loose
        odd6 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WDL_MINUTE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=75, yes='Y', team='', param='l', odd_value=2)

        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 2)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 2)
        #win
        odd5.calculate_result()
        self.assertEquals(odd5.status, Odd.FINISHED)
        self.assertEquals(odd5.result, Odd.SUCCESS)
        self.assertEquals(odd5.result_value, 2)
        #period 2 - loose
        odd6.calculate_result()
        self.assertEquals(odd6.status, Odd.FINISHED)
        self.assertEquals(odd6.result, Odd.SUCCESS)
        self.assertEquals(odd6.result_value, 2)

    #######################################################################
    def test_odd_result_half1_full_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1/2', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.RESULT_HALF1_FULL))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1/2')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='1/2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1/2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)

    #######################################################################
    def test_odd_result_half1_full_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1/X', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='1/X', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='2/X', odd_value=3.2)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_FULL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='2/X', odd_value=3.2)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.2)

    #######################################################################
    def test_odd_result_half1_half2_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1/2', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.RESULT_HALF1_HALF2))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1/2')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='1/2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1/2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)

    #######################################################################
    def test_odd_result_half1_full_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1/2', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='1/2', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='X/2', odd_value=3.2)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.RESULT_HALF1_HALF2, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='X/2', odd_value=3.2)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.2)

    #######################################################################
    def test_odd_win_both_create(self):
        odd1 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.WIN_BOTH))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match2,
                                bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match2,
                                bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match2,
                                bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='0', odd_value=3.1)
    #######################################################################
    def test_odd_win_both_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='a', param='', odd_value=3.1)
        #yes=N
        odd4 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='a', param='', odd_value=3.1)
        #SUCCESS - team-any
        odd5 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_BOTH, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)
        #SUCCESS - team-any
        odd5.calculate_result()
        self.assertEquals(odd5.status, Odd.FINISHED)
        self.assertEquals(odd5.result, Odd.SUCCESS)
        self.assertEquals(odd5.result_value, 3.1)

    #######################################################################
    def test_odd_win_list_one_half_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.WIN_LEAST_ONE_HALF))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, 'h')
        self.assertEquals(odd1.param, '')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='h', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1', odd_value=3.1)
    #######################################################################
    def test_odd_win_list_one_half_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='a', param='', odd_value=3.1)
        #yes=N
        odd4 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.WIN_LEAST_ONE_HALF, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='a', param='', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_win_to_nil_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.WIN_TO_NIL))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, 'h')
        self.assertEquals(odd1.param, '')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='h', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1', odd_value=3.1)
    #######################################################################
    def test_odd_win_to_nill_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='h', param='', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='N', team='h', param='', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='h', param='', odd_value=3.1)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='N', team='h', param='', odd_value=3.1)
        #SUCCESS - any team
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.WIN_TO_NIL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='', param='', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)
        #SUCCESS - any team
        odd5.calculate_result()
        self.assertEquals(odd5.status, Odd.FINISHED)
        self.assertEquals(odd5.result, Odd.SUCCESS)
        self.assertEquals(odd5.result_value, 3.1)

    #######################################################################
    def test_odd_correct_score_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='2:1,1:1', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.CORRECT_SCORE))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '2:1,1:1')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='2:1,1:1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='a', param='2:1,1:1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
    #######################################################################
    def test_odd_correct_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='', param='1:0,1:1', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='N', team='', param='1:0,1:1', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='1:1', odd_value=3.1)
        #yes=N
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='N', team='', param='1:1', odd_value=3.1)
        #SUCCESS 
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CORRECT_SCORE, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='1:2', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #yes=N
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)
        #SUCCESS - any team
        odd5.calculate_result()
        self.assertEquals(odd5.status, Odd.FINISHED)
        self.assertEquals(odd5.result, Odd.SUCCESS)
        self.assertEquals(odd5.result_value, 3.1)

    #######################################################################
    def test_odd_total_even_odd_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='even', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_EVEN_ODD))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, 'even')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='even', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='even', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
    #######################################################################
    def test_odd_total_even_odd_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='even', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='even', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='h', param='even', odd_value=3.1)
        #SUCCESS - both
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_EVEN_ODD, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='odd', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.status, Odd.FINISHED)
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.status, Odd.FINISHED)
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.status, Odd.FINISHED)
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #SUCCESS - any team
        odd4.calculate_result()
        self.assertEquals(odd4.status, Odd.FINISHED)
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_total_over_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.75', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_OVER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.75')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='N', team='', param='1.75', odd_value=3.1)
    #######################################################################
    def test_odd_total_over_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='1.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='h', param='1.5', odd_value=3.1)
        #various parameters
        odd_value = Decimal(3.11)
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='2.5', odd_value=odd_value)
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='2.75', odd_value=odd_value)
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3', odd_value=odd_value)
        odd6 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3.25', odd_value=odd_value)
        odd7 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3.5', odd_value=odd_value)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #various parameters
        odd3.calculate_result()
        expected_result = (odd_value/Decimal(2) + odd_value/Decimal(2))
        self.assertEquals(odd3.result, Odd.SUCCESS)
        self.assertEquals(odd3.result_value, expected_result)
        odd4.calculate_result()
        expected_result = (odd_value/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd4.result, Odd.PART_SUCCESS)
        self.assertEquals(odd4.result_value, expected_result)
        odd5.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd5.result, Odd.RETURN)
        self.assertEquals(odd5.result_value, expected_result)
        odd6.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd6.result, Odd.PART_FAIL)
        self.assertEquals(odd6.result_value, expected_result)
        odd7.calculate_result()
        expected_result = (Decimal('0')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd7.result, Odd.FAIL)
        self.assertEquals(odd7.result_value, expected_result)

    #######################################################################
    def test_odd_total_under_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.75', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_UNDER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.75')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='N', team='', param='1.75', odd_value=3.1)
    #######################################################################
    def test_odd_total_under_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='4.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='h', param='0.5', odd_value=3.1)
        #various parameters
        odd_value = Decimal(3.11)
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='2.5', odd_value=odd_value)
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='2.75', odd_value=odd_value)
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3', odd_value=odd_value)
        odd6 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3.25', odd_value=odd_value)
        odd7 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='3.5', odd_value=odd_value)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #various parameters
        odd3.calculate_result()
        expected_result = (Decimal('0')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, expected_result)
        odd4.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd4.result, Odd.PART_FAIL)
        self.assertEquals(odd4.result_value, expected_result)
        odd5.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd5.result, Odd.RETURN)
        self.assertEquals(odd5.result_value, expected_result)
        odd6.calculate_result()
        expected_result = (odd_value/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd6.result, Odd.PART_SUCCESS)
        self.assertEquals(odd6.result_value, expected_result)
        odd7.calculate_result()
        expected_result = (odd_value/Decimal(2) + odd_value/Decimal(2))
        self.assertEquals(odd7.result, Odd.SUCCESS)
        self.assertEquals(odd7.result_value, expected_result)

    #######################################################################
    def test_odd_total_both_halves_over_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_BOTH_HALVES_OVER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.5')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.25', odd_value=3.1)
    #######################################################################
    def test_odd_total_both_halves_over_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='0.5', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='0.5', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        #SUCCESS - home
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='0.5', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #SUCCESS - home
        odd4.calculate_result()
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_total_both_halves_under_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_BOTH_HALVES_UNDER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.5')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.25', odd_value=3.1)
    #######################################################################
    def test_odd_total_both_halves_under_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='1.5', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='1.5', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='0.5', odd_value=3.1)
        #SUCCESS - away
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_BOTH_HALVES_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='a', param='2.5', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #SUCCESS - away
        odd4.calculate_result()
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_total_over_minutes_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='', param='1.75', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_OVER_MINUTES))
        self.assertEquals(odd1.period, 15)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.75')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='wrong', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='N', team='', param='1.75', odd_value=3.1)
    #######################################################################
    def test_odd_total_over_minutes_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='0.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='1.5', odd_value=3.1)
        #FAIL2
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=30, yes='Y', team='h', param='0.5', odd_value=3.1)
        #SUCCESS2
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_OVER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=75, yes='Y', team='', param='0.5', odd_value=3.1)
        #calculate
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        odd4.calculate_result()
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_total_under_minutes_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='', param='1.75', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL_UNDER_MINUTES))
        self.assertEquals(odd1.period, 15)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.75')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='wrong', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='N', team='', param='1.75', odd_value=3.1)
    #######################################################################
    def test_odd_total_under_minutes_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='1.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='0.5', odd_value=3.1)
        #FAIL2
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL_UNDER_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=60, yes='Y', team='', param='1.5', odd_value=3.1)
        #calculate
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)

    #######################################################################
    def test_odd_total_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1,2', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.TOTAL))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1,2')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=12, yes='Y', team='', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='odd', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1,1.5', odd_value=3.1)
    #######################################################################
    def test_odd_total_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='1,2', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='1,2', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1,2,3', odd_value=3.1)
        #SUCCESS - away
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.TOTAL, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='a', param='2', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #SUCCESS - away
        odd4.calculate_result()
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)

    #######################################################################
    def test_odd_handicap_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='1.75', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.HANDICAP))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, 'h')
        self.assertEquals(odd1.param, '+1.75')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='h', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.75', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='-1.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='N', team='a', param='1.75', odd_value=3.1)
    #######################################################################
    def test_odd_handicap_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='0.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='a', param='-0.5', odd_value=3.1)
        #various parameters
        odd_value = Decimal(3.11)
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='a', param='-0.5', odd_value=odd_value)
        odd4 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='a', param='-0.75', odd_value=odd_value)
        odd5 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='a', param='-1', odd_value=odd_value)
        odd6 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='a', param='-1.25', odd_value=odd_value)
        odd7 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='a', param='-1.5', odd_value=odd_value)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #various parameters
        odd3.calculate_result()
        expected_result = (odd_value/Decimal(2) + odd_value/Decimal(2))
        self.assertEquals(odd3.result, Odd.SUCCESS)
        self.assertEquals(odd3.result_value, expected_result)
        odd4.calculate_result()
        expected_result = (odd_value/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd4.result, Odd.PART_SUCCESS)
        self.assertEquals(odd4.result_value, expected_result)
        odd5.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('1')/Decimal(2))
        self.assertEquals(odd5.result, Odd.RETURN)
        self.assertEquals(odd5.result_value, expected_result)
        odd6.calculate_result()
        expected_result = (Decimal('1')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd6.result, Odd.PART_FAIL)
        self.assertEquals(odd6.result_value, expected_result)
        odd7.calculate_result()
        expected_result = (Decimal('0')/Decimal(2) + Decimal('0')/Decimal(2))
        self.assertEquals(odd7.result, Odd.FAIL)
        self.assertEquals(odd7.result_value, expected_result)

    #######################################################################
    def test_odd_handicap_minutes_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='0.5', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.HANDICAP_MINUTES))
        self.assertEquals(odd1.period, 15)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, 'h')
        self.assertEquals(odd1.param, '+0.50')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='h', param='0.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='0.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='h', param='-0.125', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid yes-no param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='N', team='a', param='0.5', odd_value=3.1)
    #######################################################################
    def test_odd_handicap_minutes_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='h', param='-0.5', odd_value=3.1)
        #FAIL
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=15, yes='Y', team='a', param='0', odd_value=3.1)
        #SUCCESS 2
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.HANDICAP_MINUTES, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=30, yes='Y', team='a', param='0.5', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.SUCCESS)
        self.assertEquals(odd3.result_value, 3.1)

    #######################################################################
    def test_odd_consecutive_goals_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='2', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.CONSECUTIVE_GOALS))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '2')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=1, yes='Y', team='', param='2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='wrong', param='2', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='odd', odd_value=3.1)
    #######################################################################
    def test_odd_consecutive_goals_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='2', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='h', param='2', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='h', param='3', odd_value=3.1)
        #SUCCESS - any
        odd4 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='2', odd_value=3.1)
        #FAIL - away
        odd5 = Odd.create(match=self.match2,
                            bet_type_slug=BetType.CONSECUTIVE_GOALS, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='a', param='2', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)
        #SUCCESS - any team
        odd4.calculate_result()
        self.assertEquals(odd4.result, Odd.SUCCESS)
        self.assertEquals(odd4.result_value, 3.1)
        #FAIL - away
        odd5.calculate_result()
        self.assertEquals(odd5.result, Odd.FAIL)
        self.assertEquals(odd5.result_value, 0)

    #######################################################################
    def test_odd_itotal_both_over_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.ITOTAL_BOTH_OVER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.5')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='odd', odd_value=3.1)
    #######################################################################
    def test_odd_itotal_both_over_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='N', team='', param='1.5', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_OVER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='', param='0.5', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)

    #######################################################################
    def test_odd_itotal_both_under_create(self):
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=0, yes='Y', team='', param='1.5', odd_value=3.1)
        self.assertEquals(odd1.bet_type, BetType.objects.get(slug=BetType.ITOTAL_BOTH_UNDER))
        self.assertEquals(odd1.period, 0)
        self.assertEquals(odd1.yes, 'Y')
        self.assertEquals(odd1.team, '')
        self.assertEquals(odd1.param, '1.5')
        self.assertEquals(odd1.odd_value, 3.1)
        #check errors
        with self.assertRaisesRegex(ValueError, 'Invalid period param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=15, yes='Y', team='', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid team param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='h', param='1.5', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='1', odd_value=3.1)
        with self.assertRaisesRegex(ValueError, 'Invalid odd param'):
            odd = Odd.create(match=self.match1,
                                bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                                load_source=self.load_source_2, bookie=self.bookie, 
                                period=0, yes='Y', team='', param='odd', odd_value=3.1)
    #######################################################################
    def test_odd_itotal_both_under_calculate(self):
        #SUCCESS
        odd1 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='Y', team='', param='1.5', odd_value=3.1)
        #yes=N
        odd2 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=1, yes='N', team='', param='1.5', odd_value=3.1)
        #FAIL
        odd3 = Odd.create(match=self.match1,
                            bet_type_slug=BetType.ITOTAL_BOTH_UNDER, value_type_slug=ValueType.MAIN,
                            load_source=self.load_source_2, bookie=self.bookie, 
                            period=2, yes='Y', team='', param='1.5', odd_value=3.1)
        #calculate
        #SUCCESS
        odd1.calculate_result()
        self.assertEquals(odd1.result, Odd.SUCCESS)
        self.assertEquals(odd1.result_value, 3.1)
        #yes=N
        odd2.calculate_result()
        self.assertEquals(odd2.result, Odd.FAIL)
        self.assertEquals(odd2.result_value, 0)
        #FAIL
        odd3.calculate_result()
        self.assertEquals(odd3.result, Odd.FAIL)
        self.assertEquals(odd3.result_value, 0)

