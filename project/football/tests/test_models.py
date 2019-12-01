from django.test import TestCase

from project.core.factories import get_country 
from project.core.models import Sport, LoadSource, TeamType

from ..factories import get_football, get_football_team, get_football_referee
from ..models import FootballLeague, FootballTeam, FootballReferee


def prepare_data(obj):
    obj.load_source = LoadSource.objects.get(slug=LoadSource.SRC_ESPN)


#######################################################################################
class FootballLeagueModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    def test_create_league(self):
        league_test_create = FootballLeague.objects.create(name = 'test create league', team_type = TeamType.objects.get(slug=TeamType.UNKNOWN))
        self.assertTrue(league_test_create.slug.startswith('test-create-league'))
        football = Sport.objects.get(league=league_test_create)
        self.assertEquals(football.slug, 'football')

    def test_save_league(self):
        league_save_create = FootballLeague(name = 'test save league', team_type = TeamType.objects.get(slug=TeamType.UNKNOWN))
        league_save_create.save()
        self.assertTrue(league_save_create.slug.startswith('test-save-league'))
        football = Sport.objects.get(league=league_save_create)
        self.assertEquals(football.slug, 'football')

    def test_get_or_create(self):
        football = get_football()
        russia = get_country('rus')
        league_slug = 'league-get-or-create'
        league_new = FootballLeague.get_or_create(slug=league_slug, country=russia, name='League get or create', 
                                                  load_source=self.load_source)
        self.assertEquals(league_new.sport, football)
        league_get = FootballLeague.get_or_create(slug=league_slug, country=russia, name='League get or create',
                                                  load_source=self.load_source)
        self.assertEquals(league_new, league_get)


#######################################################################################
class FootballTeamModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_create_team(self):
        russia = get_country('rus')
        football = get_football()
        team_test_create = FootballTeam.objects.create(name = 'test create team', country=russia, team_type = TeamType.objects.get(slug=TeamType.UNKNOWN))
        created_team = get_football_team(country=russia, slug='test-create-team')
        self.assertIsNotNone(created_team, 'Cant find team with slug "test-create-team"')
        self.assertEquals(created_team.sport, football, 'Created team is not football team')

    def test_save_team(self):
        russia = get_country('rus')
        football = get_football()
        team_test_save = FootballTeam(name = 'test save team', country=russia, team_type = TeamType.objects.get(slug=TeamType.UNKNOWN))
        team_test_save.save()
        saved_team = get_football_team(country=russia, slug='test-save-team')
        self.assertIsNotNone(saved_team, 'Cant find team with slug "test-save-team"')
        self.assertEquals(saved_team.sport, football, 'Saved team is not football team')


#######################################################################################
class FootballRefereeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def test_create_referee(self):
        russia = get_country('rus')
        football = get_football()
        referee_test_create = FootballReferee.objects.create(name = 'test create referee', country=russia)
        created_referee = get_football_referee(country=russia, slug='test-create-referee')
        self.assertIsNotNone(created_referee, 'Cant find referee with slug "test-create-referee"')
        self.assertEquals(created_referee.sport, football, 'Created referee is not football referee')

    def test_save_referee(self):
        russia = get_country('rus')
        football = get_football()
        referee_test_save = FootballReferee(name = 'test save referee', country=russia)
        referee_test_save.save()
        saved_referee = get_football_referee(country=russia, slug='test-save-referee')
        self.assertIsNotNone(saved_referee, 'Cant find refereee with slug "test-save-refereee"')
        self.assertEquals(saved_referee.sport, football, 'Saved refereee is not football refereee')

