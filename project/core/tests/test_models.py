from datetime import date, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError

from core.factories import get_sport, get_country, get_team

from core.models import (
    Loadable, ObjectLoadSource,
    Sport, 
    LoadSource, 
    Country, CountryLoadSource,
    TeamType, 
    League, LeagueLoadSource, 
    Season,
    Team,
    TeamMembership,
    Referee,
    Match, MatchReferee,
    )


def prepare_data(obj):
    obj.load_source = LoadSource.objects.get(slug=LoadSource.SRC_ESPN)
    obj.football = Sport.objects.get(slug=Sport.FOOTBALL)
    obj.sport = obj.football
    obj.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.unknown_country = Country.objects.get(slug='na')
    obj.load_source_1, created = LoadSource.objects.get_or_create(
                                                  slug = 'test_load_source_1', 
                                                  sport = obj.football,
                                                  defaults={'name':'test_load_source_1', 'reliability':1}
                                                  )
    obj.load_source_2, created = LoadSource.objects.get_or_create(
                                                  slug = 'test_load_source_2', 
                                                  sport = obj.football,
                                                  defaults={'name':'test_load_source_2', 'reliability':2}
                                                  )
    obj.load_source_3, created = LoadSource.objects.get_or_create(
                                                  slug = 'test_load_source_3', 
                                                  sport = obj.football,
                                                  defaults={'name':'test_load_source_3', 'reliability':3}
                                                  )


#######################################################################################
######  Country
#######################################################################################
class CountryModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_country_get_or_create(self):
        try:
            russia = Country.objects.get(slug='rus')
        except Country.DoesNotExist:
            pass
        except:
            self.assertTrue(False, 'Russia does not exist')
        # test get - get old country
        old_country = Country.get_or_create('rus', self.load_source)
        self.assertEquals(old_country, russia)
        old_country_load = CountryLoadSource.objects.get(slug='rus', load_source=self.load_source)
        self.assertEquals(old_country_load.status, ObjectLoadSource.ACTIVE)
        self.assertEquals(old_country_load.country_obj, russia)
        # test create - create new country
        new_country = Country.get_or_create('test_get_or_create_country', self.load_source)
        self.assertEquals(new_country.load_status, Loadable.UNCONFIRMED)
        new_country2 = Country.get_or_create('test_get_or_create_country', self.load_source)
        self.assertEquals(new_country, new_country2)
        self.assertEquals(new_country.load_source, self.load_source)
        new_country_load = CountryLoadSource.objects.get(slug='test_get_or_create_country', load_source=self.load_source)
        self.assertEquals(new_country_load.status, ObjectLoadSource.ACTIVE)
        self.assertEquals(new_country_load.country_obj, new_country)


    #######################################################################
    def test_country_confirm(self):
        new_country = Country.get_or_create('test_confirm_country', self.load_source_1)
        self.assertEquals(new_country.load_status, Loadable.UNCONFIRMED)
        self.assertEquals(new_country.load_source, self.load_source_1)
        #confirm with change load_source
        new_country.confirm(self.load_source_2)
        self.assertEquals(new_country.load_status, Loadable.CONFIRMED)
        self.assertEquals(new_country.load_source, self.load_source_2)
        #already confirmed - can't change load_source with higher reliability
        new_country.confirm(self.load_source_3)
        self.assertEquals(new_country.load_source, self.load_source_2)
        #already confirmed -  change load_source with lower reliability
        new_country.confirm(self.load_source_1)
        self.assertEquals(new_country.load_source, self.load_source_1)


    #######################################################################
    def test_country_merge(self):
        country_src = Country.get_or_create('test_merge_country 1', self.load_source_1)
        country_src_2 = Country.get_or_create('test_merge_country 3', self.load_source_3)
        src_pk = country_src.pk
        src_2_pk = country_src_2.pk
        league_src_1 = League.get_or_create(name='test_merge_league 1',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_1
                                            )
        league_src_2 = League.get_or_create(name='test_merge_league 2',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_2
                                            )
        league_src_1_pk = league_src_1.pk
        league_src_2_pk = league_src_2.pk
        team_src_1 = Team.get_or_create(name='test_merge_team 1',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_1
                                            )
        team_src_2 = Team.get_or_create(name='test_merge_team 2',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_2
                                            )
        team_src_1_pk = team_src_1.pk
        team_src_2_pk = team_src_2.pk
        referee_src_1 = Referee.get_or_create(name='test_merge_referee 1',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_1
                                            )
        referee_src_2 = Referee.get_or_create(name='test_merge_referee 2',
                                            sport=self.football,
                                            country=country_src, 
                                            load_source=self.load_source_2
                                            )
        referee_src_1_pk = referee_src_1.pk
        referee_src_2_pk = referee_src_2.pk

        country_dst = Country.get_or_create('test_merge_country 2', self.load_source_2)
        dst_pk = country_dst.pk
        league_dst_2 = League.get_or_create(name='test_merge_league 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        league_dst_2_pk = league_dst_2.pk
        team_dst_2 = Team.get_or_create(name='test_merge_team 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        team_dst_2_pk = team_dst_2.pk
        referee_dst_2 = Referee.get_or_create(name='test_merge_referee 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        referee_dst_2_pk = referee_dst_2.pk

        #merge
        country_src.merge_to(country_dst)
        country_src_2.merge_to(country_dst)
        country_dst = Country.objects.get(pk=dst_pk)
        self.assertEquals(country_dst.name, 'test_merge_country 1')

        #Both 'test_merge_country 1' and 'test_merge_country 2' point to country_dst 
        country_load_source = CountryLoadSource.objects.get(country_obj=country_dst,
                                                            slug='test_merge_country-1' 
                                                            )
        country_load_source = CountryLoadSource.objects.get(country_obj=country_dst,
                                                            slug='test_merge_country-2' 
                                                            )
        country_load_source = CountryLoadSource.objects.get(country_obj=country_dst,
                                                            slug='test_merge_country-3' 
                                                            )
        country_1 = Country.get_or_create('test_merge_country 1', self.load_source_1)
        self.assertEquals(country_1, country_dst)
        country_2 = Country.get_or_create('test_merge_country 2', self.load_source_2)
        self.assertEquals(country_2, country_dst)
        country_3 = Country.get_or_create('test_merge_country 3', self.load_source_3)
        self.assertEquals(country_3, country_dst)

        with self.assertRaises(Country.DoesNotExist):
            country = Country.objects.get(pk=src_pk)
        with self.assertRaises(Country.DoesNotExist):
            country = Country.objects.get(pk=src_2_pk)
        with self.assertRaises(CountryLoadSource.DoesNotExist):
            country = CountryLoadSource.objects.get(country_obj=src_pk)
        with self.assertRaises(CountryLoadSource.DoesNotExist):
            country = CountryLoadSource.objects.get(country_obj=src_2_pk)

        #check leagues
        league_src_1 = League.get_or_create(name='test_merge_league 1',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_1
                                            )
        self.assertEquals(league_src_1.pk, league_src_1_pk, 'league_src_1 did not change')
        league_src_2 = League.get_or_create(name='test_merge_league 2',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_2
                                            )
        self.assertEquals(league_src_2.pk, league_dst_2_pk, 'league_src_2 shuold chande to league_dst_2_pk')
        league_dst_2 = League.get_or_create(name='test_merge_league 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        self.assertEquals(league_dst_2.pk, league_dst_2_pk)

        #check teams
        team_src_1 = Team.get_or_create(name='test_merge_team 1',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_1
                                            )
        self.assertEquals(team_src_1.pk, team_src_1_pk, 'team_src_1 did not change')
        team_src_2 = Team.get_or_create(name='test_merge_team 2',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_2
                                            )
        self.assertEquals(team_src_2.pk, team_dst_2_pk, 'team_src_2 shuold chande to team_dst_2_pk')
        team_dst_2 = Team.get_or_create(name='test_merge_team 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        self.assertEquals(team_dst_2.pk, team_dst_2_pk)

        #check referee
        referee_src_1 = Referee.get_or_create(name='test_merge_referee 1',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_1
                                            )
        self.assertEquals(referee_src_1.pk, referee_src_1_pk, 'referee_src_1 did not change')
        referee_src_2 = Referee.get_or_create(name='test_merge_referee 2',
                                            sport=self.football,
                                            country=country_1, 
                                            load_source=self.load_source_2
                                            )
        self.assertEquals(referee_src_2.pk, referee_dst_2_pk, 'team_src_2 shuold chande to referee_dst_2_pk')
        referee_dst_2 = Referee.get_or_create(name='test_merge_referee 2',
                                            sport=self.football,
                                            country=country_dst, 
                                            load_source=self.load_source_3
                                            )
        self.assertEquals(referee_dst_2.pk, referee_dst_2_pk)


#######################################################################################
######  League
#######################################################################################
class LeagueModelTest(TestCase):

    def setUp(self):
        prepare_data(self)
        self.league = League.objects.create(
            slug='first', 
            name='Premier Liga', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        self.season1 = Season.objects.create(
            name='2017/2018',
            league=self.league,
            start_date=date(2017, 8, 1),
            end_date=date(2018, 6, 10)
        )
        self.season2 = Season.objects.create(
            name='2018/2019',
            league=self.league,
            start_date=date(2018, 8, 2),
            end_date=date(2019, 6, 8)
        )

    #######################################################################
    def test_empty_country(self):
        league_empty_country = League.objects.create(
            name='Empty Country League', 
            sport=Sport.objects.get(slug=Sport.FOOTBALL)
        )
        self.assertTrue(league_empty_country.slug.startswith('empty-country-league'))
        unknown_country = Country.objects.get(slug='na')
        self.assertEquals(league_empty_country.country, unknown_country)


    #######################################################################
    def test_unique_league(self):
        sport = Sport.objects.get(slug=Sport.FOOTBALL)
        country = Country.objects.get(slug='rus')
        with self.assertRaises(IntegrityError):
            league = League.objects.create(
                slug='first', 
                name='Premier Liga', 
                sport=sport, country=country
            )

    #######################################################################
    def test_league_get_season(self):
        league = self.league
        season_2017 = league.get_season(date(2017, 9, 1))
        self.assertEquals(season_2017.name, '2017/2018')
        season_none = league.get_season(date(2017, 7, 1))
        self.assertIsNone(season_none)
        season_2018 = league.get_season(date(2018, 8, 2))
        self.assertEquals(season_2018.name, '2018/2019')

    #######################################################################
    def test_league_get_or_create_season(self):
        league = self.league
        season = league.get_or_create_season( 
                                       start_date=date(2017,6,1), 
                                       end_date=date(2018,5,1), 
                                       load_source=self.load_source_2)
        self.assertEquals(season.league, league)

    #######################################################################
    def test_league_get_or_create(self):
        league_old = League.create(
                                name='test_get_or_create_league_1',
                                team_type=self.team_type,
                                sport=self.sport,
                                country=self.country,
                                )
        league_get = League.get_or_create(
                                name='test_get_or_create_league_1',
                                sport=self.sport,
                                country=self.country,
                                load_source=self.load_source,
                                )
        self.assertEquals(league_old.pk, league_get.pk, 'should get the same league')

        league_new = League.get_or_create(
                                name='test_get_or_create_league_2',
                                team_type=self.team_type,
                                sport=self.sport,
                                country=self.country,
                                load_source=self.load_source,
                                )
        self.assertEquals(league_new.load_status, Loadable.UNCONFIRMED)
        self.assertEquals(league_new.country, self.country)
        self.assertEquals(league_new.team_type, self.team_type)
        self.assertEquals(league_new.sport, self.sport)

        league_load = LeagueLoadSource.objects.get(
                        slug='test_get_or_create_league_2', 
                        load_source=self.load_source,
                        sport=self.sport,
                        country=self.country
                        )
        self.assertEquals(league_load.status, ObjectLoadSource.ACTIVE)
        self.assertEquals(league_load.league, league_new)

    #######################################################################
    def test_league_confirm(self):
        new_league = Country.get_or_create('test_confirm_league', self.load_source_1)
        self.assertEquals(new_league.load_status, Loadable.UNCONFIRMED)
        self.assertEquals(new_league.load_source, self.load_source_1)
        #confirm with change load_source
        new_league.confirm(self.load_source_2)
        self.assertEquals(new_league.load_status, Loadable.CONFIRMED)
        self.assertEquals(new_league.load_source, self.load_source_2)
        #already confirmed - can't change load_source with higher reliability
        new_league.confirm(self.load_source_3)
        self.assertEquals(new_league.load_source, self.load_source_2)
        #already confirmed -  change load_source with lower reliability
        new_league.confirm(self.load_source_1)
        self.assertEquals(new_league.load_source, self.load_source_1)


    #######################################################################
    def test_league_merge(self):
        team1 = Team.get_or_create(
            name='team league_merge 1', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team2 = Team.get_or_create(
            name='team league_merge 2', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        league_src = League.get_or_create(name='test_merge_league 1', 
                                          sport=self.sport, 
                                          load_source=self.load_source_1,
                                          )
        league_src_2 = League.get_or_create(name='test_merge_league 3', 
                                            sport=self.sport, 
                                            load_source=self.load_source_3
                                            )
        src_pk = league_src.pk
        src_2_pk = league_src_2.pk
        match1 = Match.get_or_create(
                                league=league_src, team_h=team1, team_a=team2, 
                                match_date=date(2017,10,1), 
                                load_source=self.load_source_1
                                )
        match2 = Match.get_or_create(
                                league=league_src, team_h=team1, team_a=team2, 
                                match_date=date(2016,10,1), 
                                load_source=self.load_source_1
                                )

        league_dst = League.get_or_create(name='test_merge_league 2', 
                                          sport=self.sport, 
                                          load_source=self.load_source_2
                                          )
        dst_pk = league_dst.pk
        season1 = Season.get_or_create(league_dst, 
                                       start_date=date(2017,6,1), 
                                       end_date=date(2018,5,1), 
                                       load_source=self.load_source_2)

        #merge
        league_src.merge_to(league_dst)
        league_src_2.merge_to(league_dst)
        league_dst = League.objects.get(pk=dst_pk)
        self.assertEquals(league_dst.name, 'test_merge_league 1')

        #Both 'test_merge_league 1' and 'test_merge_league 2' point to league_dst 
        league_load_source = LeagueLoadSource.objects.get(league=league_dst,
                                                          sport=self.sport, 
                                                          load_source=self.load_source_1,
                                                          slug='test_merge_league-1' 
                                                          )
        league_load_source = LeagueLoadSource.objects.get(league=league_dst,
                                                          sport=self.sport, 
                                                          load_source=self.load_source_2,
                                                          slug='test_merge_league-2' 
                                                          )
        league_load_source = LeagueLoadSource.objects.get(league=league_dst,
                                                          sport=self.sport, 
                                                          load_source=self.load_source_3,
                                                          slug='test_merge_league-3' 
                                                          )
        league_1 = League.get_or_create(name='test_merge_league 1', 
                                        sport=self.sport, 
                                        load_source=self.load_source_1)
        self.assertEquals(league_1, league_dst)
        league_2 = League.get_or_create(name='test_merge_league 2', 
                                        sport=self.sport, 
                                        load_source=self.load_source_2)
        self.assertEquals(league_2, league_dst)
        league_3 = League.get_or_create(name='test_merge_league 3', 
                                        sport=self.sport, 
                                        load_source=self.load_source_3)
        self.assertEquals(league_3, league_dst)

        with self.assertRaises(League.DoesNotExist):
            league = League.objects.get(pk=src_pk)
        with self.assertRaises(League.DoesNotExist):
            league = League.objects.get(pk=src_2_pk)
        with self.assertRaises(LeagueLoadSource.DoesNotExist):
            league = LeagueLoadSource.objects.get(league=src_pk)
        with self.assertRaises(LeagueLoadSource.DoesNotExist):
            league = LeagueLoadSource.objects.get(league=src_2_pk)

        #check teams
        match1.refresh_from_db()
        match2.refresh_from_db()
        self.assertEquals(match1.league, league_dst)
        self.assertEquals(match1.season, season1)
        self.assertEquals(match2.league, league_dst)
        self.assertIsNone(match2.season)

    #######################################################################
    def test_league_process_empty_season(self):
        team1 = Team.get_or_create(
            name='team league_process_empty_season 1', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team2 = Team.get_or_create(
            name='team league_process_empty_season 2', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        match1 = Match.get_or_create(
                                league=self.league, team_h=team1, team_a=team2, 
                                match_date=date(2017,10,1), 
                                load_source=self.load_source_1
                                )
        match2 = Match.get_or_create(
                                league=self.league, team_h=team1, team_a=team2, 
                                match_date=date(2011,10,1), 
                                load_source=self.load_source_1
                                )
        match1.refresh_from_db()
        match2.refresh_from_db()
        self.assertEquals(match1.season, self.season1)
        self.assertIsNone(match2.season)

        season = self.league.get_or_create_season(
                                                  start_date=date(2011,6,1), 
                                                  end_date=date(2012,5,1), 
                                                  load_source=self.load_source_1)
        self.assertFalse(TeamMembership.objects.filter(team=team1,season=season).exists())
        self.assertFalse(TeamMembership.objects.filter(team=team2,season=season).exists())
        self.league.process_empty_season()
        match1.refresh_from_db()
        match2.refresh_from_db()
        self.assertEquals(match1.season, self.season1)
        self.assertEquals(match2.season, season)
        self.assertTrue(TeamMembership.objects.filter(team=team1,season=season).exists())
        self.assertTrue(TeamMembership.objects.filter(team=team2,season=season).exists())



#######################################################################################
######  Season
#######################################################################################
class SeasonModelTest(TestCase):
    def setUp(self):
        prepare_data(self)
        self.league1 = League.get_or_create(name='test_season_league 1',
                                            sport=self.football,
                                            country=self.country, 
                                            load_source=self.load_source_2
                                            )
        self.league2 = League.get_or_create(name='test_season_league 2',
                                            sport=self.football,
                                            country=self.country, 
                                            load_source=self.load_source_2
                                            )

    #######################################################################
    def test_season_get_or_create(self):
        season1 = Season.get_or_create(self.league1, 
                                       start_date=date(2017,6,1), 
                                       end_date=date(2018,5,1), 
                                       load_source=self.load_source_2)
        self.assertEquals(season1.league, self.league1)
        self.assertEquals(season1.start_date, date(2017,6,1))
        self.assertEquals(season1.end_date, date(2018,5,1))
        self.assertEquals(season1.name, r'2017\2018')
        self.assertEquals(season1.load_source, self.load_source_2)

        with self.assertRaisesRegex(ValueError, 'Incorrect season dates'):
            season2 = Season.get_or_create(self.league1, 
                                           start_date=date(2017,6,1), 
                                           end_date=date(2016,5,1), 
                                           load_source=self.load_source)

        #get season1 and don't change data
        season3 = Season.get_or_create(self.league1, 
                                       start_date=date(2017,6,3), 
                                       end_date=date(2018,5,3), 
                                       load_source=self.load_source_3)
        self.assertEquals(season3, season1)
        self.assertEquals(season3.start_date, season1.start_date)
        self.assertEquals(season3.end_date, season1.end_date)
        self.assertEquals(season3.name, season1.name)

        #get season1 and change data
        season4 = Season.get_or_create(self.league1, 
                                       start_date=date(2017,6,4), 
                                       end_date=date(2018,5,4), 
                                       load_source=self.load_source_1,
                                       name='Season 2017\\2018')
        self.assertEquals(season4, season1)
        self.assertNotEquals(season4.start_date, season1.start_date)
        self.assertNotEquals(season4.end_date, season1.end_date)
        self.assertNotEquals(season4.name, season1.name)

        #other tests
        season5 = Season.get_or_create(self.league2, 
                                       start_date=date(2017,6,4), 
                                       end_date=date(2018,5,4), 
                                       load_source=self.load_source_1,
                                       name='Season 2017\\2018')
        self.assertNotEquals(season5, season1)
        season6 = Season.get_or_create(self.league1, 
                                       start_date=date(2016,6,4), 
                                       end_date=date(2017,5,4), 
                                       load_source=self.load_source_1,
                                       name='Season 2016\\2017')
        self.assertNotEquals(season6, season1)

    #######################################################################
    def test_season_change_league(self):
        #league 1
        league_1 = League.get_or_create(name='test_season_change_league 1', 
                                        sport=self.sport, 
                                        load_source=self.load_source_1)
        season_1 = league_1.get_or_create_season(start_date=date(2016,6,1), 
                                                 end_date=date(2017,5,1), 
                                                 load_source=self.load_source_1)
        season_1_pk = season_1.pk
        team_11 = Team.get_or_create(name='test_season_change_team 11', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        team_12 = Team.get_or_create(name='test_season_change_team 12', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        memberships_11 = TeamMembership.objects.create(season=season_1, team=team_11)
        memberships_12 = TeamMembership.objects.create(season=season_1, team=team_12)
        match_1 = Match.get_or_create(
                                league=league_1, team_h=team_11, team_a=team_12, 
                                match_date=date(2016,6,1), 
                                load_source=self.load_source_1
                                )
        self.assertEquals(match_1.season, season_1)

        #league 2
        league_2 = League.get_or_create(name='test_season_change_league 2', 
                                        sport=self.sport, 
                                        load_source=self.load_source_2)
        season_2 = league_2.get_or_create_season(start_date=date(2017,6,1), 
                                                 end_date=date(2018,5,1), 
                                                 load_source=self.load_source_2)
        season_2_pk = season_2.pk
        team_21 = Team.get_or_create(name='test_season_change_team 21', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        team_22 = Team.get_or_create(name='test_season_change_team 22', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        memberships_21 = TeamMembership.objects.create(season=season_2, team=team_21)
        memberships_22 = TeamMembership.objects.create(season=season_2, team=team_22)
        match_2 = Match.get_or_create(
                                league=league_2, team_h=team_21, team_a=team_22, 
                                match_date=date(2017,6,1), 
                                load_source=self.load_source_2
                                )
        self.assertEquals(match_2.season, season_2)

        #league 3
        league_3 = League.get_or_create(name='test_season_change_league 3', 
                                        sport=self.sport, 
                                        load_source=self.load_source_3)
        season_3 = league_3.get_or_create_season(start_date=date(2017,6,1), 
                                                 end_date=date(2018,5,1), 
                                                 load_source=self.load_source_3)
        season_3_pk = season_3.pk
        team_31 = Team.get_or_create(name='test_season_change_team 31', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        team_32 = Team.get_or_create(name='test_season_change_team 32', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        memberships_31 = TeamMembership.objects.create(season=season_3, team=team_31)
        memberships_32 = TeamMembership.objects.create(season=season_3, team=team_32)
        match_3 = Match.get_or_create(
                                league=league_3, team_h=team_31, team_a=team_32, 
                                match_date=date(2017,6,1), 
                                load_source=self.load_source_3
                                )
        self.assertEquals(match_3.season, season_3)

        #league 4
        league_4 = League.get_or_create(name='test_season_change_league 4', 
                                        sport=self.sport, 
                                        load_source=self.load_source_1)
        season_4 = league_4.get_or_create_season(start_date=date(2017,6,1), 
                                                 end_date=date(2018,5,1), 
                                                 load_source=self.load_source_1)
        season_4_pk = season_4.pk
        team_41 = Team.get_or_create(name='test_season_change_team 41', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        team_42 = Team.get_or_create(name='test_season_change_team 42', 
                                    sport=self.sport, 
                                    country=self.country, 
                                    load_source=self.load_source_1)
        memberships_41 = TeamMembership.objects.create(season=season_4, team=team_41)
        memberships_42 = TeamMembership.objects.create(season=season_4, team=team_42)
        match_4 = Match.get_or_create(
                                league=league_4, team_h=team_41, team_a=team_42, 
                                match_date=date(2017,6,1), 
                                load_source=self.load_source_1
                                )
        self.assertEquals(match_4.season, season_4)

        #test 1
        season_1.change_league(league_2)
        season_11 = Season.objects.get(pk=season_1_pk)
        self.assertEquals(season_11.league, league_2)
        try:
            memberships_11 = TeamMembership.objects.get(team=team_11)
        except TeamMembership.DoesNotExist:
            memberships_11 = None
        self.assertIsNone(memberships_11)

        #test 2
        season_3.change_league(league_2)
        with self.assertRaises(Season.DoesNotExist):
            season_31 = Season.objects.get(pk=season_3_pk)
        try:
            memberships_31 = TeamMembership.objects.get(team=team_31)
        except TeamMembership.DoesNotExist:
            memberships_31 = None
        self.assertIsNone(memberships_31)
        match_3 = Match.get_object(league=league_3, team_h=team_31, team_a=team_32, match_date=date(2017,6,1))
        self.assertIsNone(match_3.season, 'Session was deleted than match session set to None')

        #test 3
        memberships_21 = TeamMembership.objects.get(team=team_21) #memberships exists
        season_21 = Season.objects.get(pk=season_2_pk)  #yet exists
        season_4.change_league(league_2)
        season_41 = Season.objects.get(pk=season_4_pk)
        self.assertEquals(season_41.league, league_2)
        with self.assertRaises(Season.DoesNotExist):
            season_21 = Season.objects.get(pk=season_2_pk)
        try:
            memberships_21 = TeamMembership.objects.get(team=team_21)
        except TeamMembership.DoesNotExist:
            memberships_21 = None
        self.assertIsNone(memberships_21)
        try:
            memberships_41 = TeamMembership.objects.get(team=team_41)
        except TeamMembership.DoesNotExist:
            memberships_41 = None
        self.assertIsNone(memberships_41)
        match_2 = Match.get_object(league=league_2, team_h=team_21, team_a=team_22, match_date=date(2017,6,1))
        self.assertIsNone(match_2.season, 'Session was deleted than match session set to None')

#######################################################################################
######  Team
#######################################################################################
class TeamModelTest(TestCase):
    def setUp(self):
        prepare_data(self)
        self.league = League.get_or_create(name='test_team_model_league 1',
                                            sport=self.football,
                                            country=self.country, 
                                            load_source=self.load_source_2
                                            )
        self.team = Team.objects.create(
            name='Dinamo Moscow', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )

    #######################################################################
    def test_team_slug(self):
        team = get_team(sport=self.sport,
                        country=self.country,
                        slug='dinamo-moscow'
                       )
        self.assertIsNotNone(team)

    #######################################################################
    def test_team_get_or_create(self):
        team1 = Team.get_or_create(
                                name='get_or_create_team 1', 
                                team_type=self.team_type, 
                                sport=self.sport, 
                                country=self.country, 
                                load_source=self.load_source_2
                                )
        self.assertEquals(team1.load_status, Loadable.UNCONFIRMED)
        self.assertEquals(team1.country, self.country)
        self.assertEquals(team1.team_type, self.team_type)
        self.assertEquals(team1.sport, self.sport)
        self.assertEquals(team1.slug, 'get_or_create_team-1')

        team2 = Team.get_or_create(
                                name='get_or_create_team 1', 
                                team_type=self.team_type, 
                                sport=self.sport, 
                                country=self.country, 
                                load_source=self.load_source_1
                                )
        self.assertEquals(team1, team2)

    #######################################################################
    def test_team_merge(self):
        match_date=date(2016,10,1)
        season = self.league.get_or_create_season(start_date=date(2016,6,1), 
                                                 end_date=date(2017,5,1), 
                                                 load_source=self.load_source_1)
        team1 = Team.get_or_create(
            name='team_merge 1', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team1_pk = team1.pk
        team2 = Team.get_or_create(
            name='team_merge 2', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team2_pk = team2.pk
        team3 = Team.get_or_create(
            name='team_merge 3', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team3_pk = team3.pk
        team4 = Team.get_or_create(
            name='team_merge 4', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        team4_pk = team3.pk
        match1 = Match.get_or_create(
                                league=self.league, team_h=team1, team_a=team2, 
                                match_date=match_date, 
                                load_source=self.load_source_2
                                )
        match1_pk = match1.pk
        match2 = Match.get_or_create(
                                league=self.league, team_h=team3, team_a=team2, 
                                match_date=match_date, 
                                load_source=self.load_source_2
                                )
        match2_pk = match2.pk

        #test 1
        team3.merge_to(team1)
        with self.assertRaises(Team.DoesNotExist):
            team3 = Team.objects.get(pk=team3_pk)
        with self.assertRaises(Match.DoesNotExist):
            match2 = Match.objects.get(pk=match2_pk)

        #test 2
        team2.merge_to(team4)
        match1 = Match.objects.get(pk=match1_pk)
        self.assertEquals(match1.team_h, team1)
        self.assertEquals(match1.team_a, team4)

        exists_team1 = TeamMembership.objects.filter(team=team1).exists()
        exists_team2 = TeamMembership.objects.filter(team=team2).exists()
        exists_team3 = TeamMembership.objects.filter(team=team3).exists()
        exists_team4 = TeamMembership.objects.filter(team=team4).exists()
        self.assertTrue(exists_team1)
        self.assertFalse(exists_team2)
        self.assertFalse(exists_team3)
        self.assertTrue(exists_team4)


#######################################################################################
######  Match
#######################################################################################
class MatchModelTest(TestCase):
    def setUp(self):
        prepare_data(self)
        self.league = League.get_or_create(
                                        name='test_model_match_league', 
                                        sport=self.sport, 
                                        load_source=self.load_source_1)
        self.season = self.league.get_or_create_season(
                                                  start_date=date(2016,6,1), 
                                                  end_date=date(2017,5,1), 
                                                  load_source=self.load_source_1)
        self.team1 = Team.get_or_create(
            name='math_modal_team 1', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        self.team2 = Team.get_or_create(
            name='math_modal_team 2', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        self.team3 = Team.get_or_create(
            name='math_modal_team 3', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )

    #######################################################################
    def test_match_get_or_create(self):
        match_date=date(2016,10,1)
        match1 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=match_date, 
                                load_source=self.load_source_2
                                )
        self.assertEquals(match1.league, self.league)
        self.assertEquals(match1.team_h, self.team1)
        self.assertEquals(match1.team_a, self.team2)
        self.assertEquals(match1.match_date, match_date)
        self.assertEquals(match1.load_source, self.load_source_2)
        self.assertEquals(match1.season, self.season)
        self.assertEquals(match1.status, Match.FINISHED)

        match2 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=match_date, 
                                status=Match.CANCELLED, load_source=self.load_source_2
                                )
        self.assertEquals(match2, match1)
        self.assertEquals(match2.status, Match.CANCELLED)

        match3 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=match_date, 
                                status=Match.FINISHED, load_source=self.load_source_3
                                )
        self.assertEquals(match3, match1)
        self.assertNotEquals(match3.status, Match.FINISHED)


    #######################################################################
    def test_match_get_object(self):
        match_date=date(2016,10,1)
        match1 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=match_date, 
                                load_source=self.load_source_2
                                )

        match2 = Match.get_object(league=self.league, team_h=self.team1, team_a=self.team2, 
                                  match_date=match_date)
        self.assertEquals(match2, match1)

        match3 = Match.get_object(league=self.league, team_h=self.team1, team_a=self.team2, 
                                  match_date=match_date - timedelta(days=1))
        self.assertEquals(match3, match1)

        match4 = Match.get_object(league=self.league, team_h=self.team1, team_a=self.team2, 
                                  match_date=match_date + timedelta(days=1))
        self.assertEquals(match4, match1)

        #add 2 days
        match5 = Match.get_object(league=self.league, team_h=self.team1, team_a=self.team2, 
                                  match_date=match_date + timedelta(days=2))
        self.assertIsNone(match5)

        #change teams in match
        match6 = Match.get_object(league=self.league, team_h=self.team2, team_a=self.team1, 
                                  match_date=match_date)
        self.assertIsNone(match6)

    #######################################################################
    def test_match_change_league(self):
        league_new = League.get_or_create(
                                        name='test_match_league_change', 
                                        sport=self.sport, 
                                        load_source=self.load_source_2)

        #test 1
        match1 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=date(2016,6,1), 
                                load_source=self.load_source_1
                                )
        match1_pk = match1.pk
        match1.change_league(league_new)
        match11 = Match.objects.get(pk=match1_pk)
        self.assertEquals(match11, match1)
        self.assertEquals(match11.league, league_new)

        #test 2
        match21 = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=date(2015,6,1),
                                status=Match.FINISHED,
                                load_source=self.load_source_1,
                                )
        match21_pk = match21.pk
        match22 = Match.get_or_create(
                                league=league_new, team_h=self.team1, team_a=self.team2, 
                                match_date=date(2015,6,1),
                                status=Match.CANCELLED,
                                load_source=self.load_source_2,
                                )
        match22_pk = match22.pk
        match21.change_league(league_new)
        with self.assertRaises(Match.DoesNotExist):
            #match21 doesn't exist: it merges to match22
            match21 = Match.objects.get(pk=match21_pk)
        match22 = Match.objects.get(pk=match22_pk)
        self.assertEquals(match22.status, Match.FINISHED)

    #######################################################################
    def test_match_set_referee(self):
        referee1 = Referee.get_or_create(name='referee test_match_set_referee 1',
                                         sport=self.football,
                                         country=self.country, 
                                         load_source=self.load_source_1
                                         )
        referee2 = Referee.get_or_create(name='referee test_match_set_referee 2',
                                         sport=self.football,
                                         country=self.country, 
                                         load_source=self.load_source_2
                                         )
        match = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=date(2016,6,1), 
                                load_source=self.load_source_1
                                )
        match.set_referee(referee1, load_source=self.load_source_2)
        match_referee = MatchReferee.objects.get(match=match)
        self.assertEquals(match_referee.referee, referee1)

        match.set_referee(referee2, load_source=self.load_source_3)
        match_referee = MatchReferee.objects.get(match=match)
        self.assertEquals(match_referee.referee, referee1)

        match.set_referee(referee2, load_source=self.load_source_1)
        match_referee = MatchReferee.objects.get(match=match)
        self.assertEquals(match_referee.referee, referee2)


#######################################################################################
######  Referee
#######################################################################################
class RefereeModelTest(TestCase):
    def setUp(self):
        prepare_data(self)
        self.league = League.get_or_create(name='test_referee_model_league',
                                            sport=self.football,
                                            country=self.country, 
                                            load_source=self.load_source_2
                                            )
        self.team1 = Team.get_or_create(
            name='referee_modal_team 1', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )
        self.team2 = Team.get_or_create(
            name='referee_modal_team 2', 
            team_type=self.team_type, sport=self.sport, country=self.country, load_source=self.load_source
        )

    #######################################################################
    def test_referee_merge(self):
        referee1 = Referee.get_or_create(name='referee test_referee_merge 1',
                                         sport=self.football,
                                         country=self.country, 
                                         load_source=self.load_source_1
                                         )
        referee1_pk = referee1.pk
        referee2 = Referee.get_or_create(name='referee test_referee_merge 2',
                                         sport=self.football,
                                         country=self.country, 
                                         load_source=self.load_source_2
                                         )
        referee2_pk = referee2.pk
        match = Match.get_or_create(
                                league=self.league, team_h=self.team1, team_a=self.team2, 
                                match_date=date(2016,6,1), 
                                load_source=self.load_source_1
                                )
        match.set_referee(referee1, load_source=self.load_source_2)
        referee1.merge_to(referee2)

        with self.assertRaises(Referee.DoesNotExist):
            referee1 = Referee.objects.get(pk=referee1_pk)

        referee2 = Referee.objects.get(pk=referee2_pk)
        self.assertEquals(referee2.name, 'referee test_referee_merge 1')

        match_referee = MatchReferee.objects.get(match=match)
        self.assertEquals(match_referee.referee, referee2)
        self.assertEquals(match_referee.load_source, self.load_source_2)

