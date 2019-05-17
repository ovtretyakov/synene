from datetime import date

from django.test import TestCase

from football.models import FootballSource, FootballLeague, FootballTeam
from core.models import Country, TeamType, Match 
from betting.models import Odd


def prepare_data(obj):
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


#######################################################################################
######  Odd
#######################################################################################
class OddModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_country_get_or_create(self):
        pass