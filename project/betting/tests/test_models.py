from datetime import date

from django.test import TestCase

from football.models import FootballSource, FootballLeague, FootballTeam
from core.models import Country, TeamType, Match 
from betting.models import BetType, ValueType, Odd


def prepare_data(obj):
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
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
    obj.league = FootballLeague.get_or_create(name='test_odd_league',
                                              country=obj.country, 
                                              load_source=obj.load_source_2
                                              )
    obj.team1 = FootballTeam.get_or_create(
        name='odd_modal_team 1', 
        team_type=obj.team_type, country=obj.country, load_source=obj.load_source
    )
    obj.team2 = FootballTeam.get_or_create(
        name='odd_modal_team 2', 
        team_type=obj.team_type, country=obj.country, load_source=obj.load_source
    )
    obj.match1 = Match.get_or_create(
                           league=obj.league, team_h=obj.team1, team_a=obj.team2, 
                            match_date=date(2016,7,3), 
                            load_source=obj.load_source_1
                            )
    obj.match2 = Match.get_or_create(
                           league=obj.league, team_h=obj.team1, team_a=obj.team2, 
                            match_date=date(2016,7,5), 
                            load_source=obj.load_source_1
                            )


#######################################################################################
######  Odd
#######################################################################################
class OddModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_matchstats_change_match(self):
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
        odd13 = Odd.objects.create(match = self.match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 2,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 1.5,
                                   status = Odd.WAITING,
                                   result = Odd.UNKNOWN,
                                   result_value = 0,
                                   load_source = self.load_source_2, 
                                   )
        odd13_pk = odd13.pk
        odd21 = Odd.objects.create(match = self.match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 0,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 2,
                                   status = Odd.FINISHED,
                                   result = Odd.SUCCESS,
                                   result_value = 1,
                                   load_source = self.load_source_1, 
                                   )
        odd21_pk = odd21.pk
        odd22 = Odd.objects.create(match = self.match2,
                                   bet_type = BetType.objects.get(slug=BetType.WDL),
                                   bookie = self.load_source,
                                   value_type = ValueType.objects.get(slug=ValueType.CORNER),
                                   period = 1,
                                   yes = 'Y',
                                   team = Match.COMPETITOR_HOME,
                                   param = '',
                                   odd_value = 2,
                                   status = Odd.FINISHED,
                                   result = Odd.SUCCESS,
                                   result_value = 1,
                                   load_source = self.load_source_3, 
                                   )
        odd22_pk = odd22.pk
        # 1
        odd11.change_match(self.match2)
        odd21.refresh_from_db()
        self.assertEquals(odd21.odd_value, 2)
        self.assertEquals(odd21.status, Odd.FINISHED)
        self.assertEquals(odd21.result, Odd.SUCCESS)
        self.assertEquals(odd21.result_value, 1)
        with self.assertRaises(Odd.DoesNotExist):
            odd = Odd.objects.get(pk=odd11_pk)
        # 2
        odd12.change_match(self.match2)
        odd22.refresh_from_db()
        self.assertEquals(odd22.odd_value, 1.5)
        self.assertEquals(odd22.status, Odd.WAITING)
        self.assertEquals(odd22.result, Odd.UNKNOWN)
        self.assertEquals(odd22.result_value, 0)
        with self.assertRaises(Odd.DoesNotExist):
            odd = Odd.objects.get(pk=odd12_pk)
        # 3
        odd13.change_match(self.match2)
        odd13.refresh_from_db()
        self.assertEquals(odd13.match, self.match2)
