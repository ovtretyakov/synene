from datetime import date

from django.test import TestCase

from football.models import FootballSource, FootballLeague, FootballTeam
from core.models import Country, TeamType, Match 
from betting.models import BetType, ValueType, Odd


def prepare_data(obj):
    obj.load_source = FootballSource.objects.get(slug=FootballSource.SRC_ESPN)
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
                                    name='test_model_odd_league', 
                                    load_source=obj.load_source_1)
    obj.team1 = FootballTeam.get_or_create(
        name='modal_odd_team 1', 
        team_type=obj.team_type, country=obj.country, load_source=obj.load_source
    )
    obj.team2 = FootballTeam.get_or_create(
        name='modal_odd_team 2', 
        team_type=obj.team_type, country=obj.country, load_source=obj.load_source
    )
    obj.match1 = Match.get_or_create(
                            league=obj.league, team_h=obj.team1, team_a=obj.team2, 
                            match_date=date(2016,10,3), 
                            load_source=obj.load_source_2
                            )


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

