from datetime import date

from django.test import TestCase

from football.models import FootballSource,FootballLeague,FootballTeam
from core.models import Country,TeamType,Match,MatchStats
from betting.models import Odd,BetType,ValueType



def prepare_data(obj):
    obj.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
    obj.bookie = obj.load_source
    obj.bookie.is_betting=1
    obj.bookie.save()
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
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
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=0, value=2)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=0, value=2)
    #GOALS - periods
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=1, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=1, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=2, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=2, value=2)
    #GOALS - minutes
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=15, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=15, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=30, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=30, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=45, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=45, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=60, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=60, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=75, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=75, value=1)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=90, value=0)
    MatchStats.objects.create(match=obj.match1, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=90, value=0)
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
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=0, value=3)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=0, value=1)
    #GOALS - periods
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=1, value=1)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=1, value=0)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_HOME, period=2, value=2)
    MatchStats.objects.create(match=obj.match2, stat_type=Match.GOALS, competitor=Match.COMTETITOR_AWAY, period=2, value=1)


#######################################################################################
######  Odd
#######################################################################################
class OddModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
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
