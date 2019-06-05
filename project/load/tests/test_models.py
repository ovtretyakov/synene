from datetime import datetime, date, timedelta

from django.test import TestCase
from django.utils import timezone

from core.models import Sport, TeamType, Country, League, Team, Match, MatchStats
from load.models import (
                        CommonHandler, 
                        SourceSession, 
                        SourceDetail, 
                        ErrorLog,
                        SourceDetailLeague,
                        SourceDetailMatch)
from load.exceptions import LoadError


def prepare_data(obj):
    obj.football = Sport.objects.get(slug=Sport.FOOTBALL)
    obj.sport = obj.football
    obj.team_type = TeamType.objects.get(slug=TeamType.REGULAR)
    obj.russia = Country.objects.get(slug='rus')
    obj.country = obj.russia
    obj.handler = CommonHandler.objects.get(slug=CommonHandler.SRC_ESPN)


#######################################################################################
######  CommonHandler
#######################################################################################
class CommonHandlerModelTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_common_handler_start_load(self):
        handler = self.handler
        #create old session
        old_session = SourceSession.objects.create(
                                                load_source = handler,
                                                start_time = timezone.now() - timedelta(hours=13),
                                                status = SourceSession.ERROR,
                                                match_cnt = 0,
                                                err_cnt = 0)
        result = handler.start_load()
        self.assertTrue(result)
        self.assertFalse(handler.load_continue, 'Start new session')
        self.assertNotEquals(handler.source_session, old_session)
        source_session_pk = handler.source_session.pk
        self.assertEquals(handler.source_session.status, SourceSession.IN_PROCESS)
        old_session.refresh_from_db()
        self.assertEquals(old_session.status, SourceSession.INTERRUPTED)
        #
        result = handler.start_load()
        self.assertTrue(result)
        self.assertTrue(handler.load_continue, 'Continue session')
        self.assertEquals(handler.source_session.pk, source_session_pk)

    #######################################################################
    def test_hendle_exception(self):
        handler = self.handler
        handler.start_load()
        handler.handle_exception('msg1')
        handler.handle_exception('msg2')
        handler.handle_exception('msg3')
        handler.handle_exception('msg4')
        handler.handle_exception('msg5')
        handler.handle_exception('msg6')
        handler.handle_exception('msg7')
        handler.handle_exception('msg8')
        handler.handle_exception('msg9')
        self.assertEquals(handler.source_session.status, SourceSession.IN_PROCESS)
        with self.assertRaises(LoadError):
            handler.handle_exception('msg10')
        count_errors = ErrorLog.objects.filter(source_session=handler.source_session).count()
        self.assertEquals(count_errors, 10)
        self.assertEquals(handler.source_session.err_cnt, 10)
        self.assertEquals(handler.source_session.status, SourceSession.ERROR)


    #######################################################################
    def test_common_handler_details(self):
        handler = self.handler
        detail_slug = 'test_details1'
        # 1
        result = handler.start_load(detail_slug)
        self.assertIsNotNone(handler.source_detail)
        source_session_1 = handler.source_session
        source_detail_1 = handler.source_detail
        source_detail_pk = handler.source_detail.pk
        self.assertEquals(handler.source_session.status, SourceSession.IN_PROCESS)
        self.assertEquals(handler.source_detail.status, SourceDetail.IN_PROCESS)
        self.assertEquals(handler.source_detail.slug, detail_slug)
        handler.finish_detail()
        source_detail_1.refresh_from_db()
        self.assertEquals(source_detail_1.status, SourceDetail.FINISHED)
        handler.finish_load()
        self.assertIsNone(handler.source_session)
        self.assertIsNone(handler.source_detail)
        source_session_1.refresh_from_db()
        self.assertEquals(source_session_1.status, SourceSession.FINISHED)
        # 2
        result = handler.start_load()
        self.assertTrue(result, 'success start load')
        self.assertEquals(handler.get_load_date(), date(2010, 1, 1))
        handler.set_load_date(date(2012, 2, 2))
        self.assertIsNone(handler.source_detail)
        handler.start_detail(detail_slug)
        self.assertEquals(handler.source_detail.status, SourceDetail.IN_PROCESS)
        self.assertEquals(handler.source_detail.pk, source_detail_pk)
        start_load = handler.start_or_skip_league('common_handler_details_league 1')
        start_load = handler.start_or_skip_league('common_handler_details_league 2')
        start_load = handler.start_or_skip_match('common_handler_details_team 11','common_handler_details_team 12')
        start_load = handler.start_or_skip_match('common_handler_details_team 21','common_handler_details_team 22')
        start_load = handler.start_or_skip_match('common_handler_details_team 31','common_handler_details_team 32')
        league_cnt = SourceDetailLeague.objects.filter(source_detail__load_source=handler).count()
        match_cnt = SourceDetailMatch.objects.filter(source_detail__load_source=handler).count()
        self.assertEquals(league_cnt, 2)
        self.assertEquals(match_cnt, 3)
        ## 2 - finish_detail
        handler.finish_detail()
        self.assertIsNone(handler.source_detail)
        source_detail = SourceDetail.objects.get(pk=source_detail_pk)
        self.assertEquals(source_detail.status, SourceDetail.FINISHED)
        league_cnt = SourceDetailLeague.objects.filter(source_detail__load_source=handler).count()
        match_cnt = SourceDetailMatch.objects.filter(source_detail__load_source=handler).count()
        self.assertEquals(league_cnt, 2)
        self.assertEquals(match_cnt, 3)
        ## 2 - finish_load
        handler.finish_load()
        league_cnt = SourceDetailLeague.objects.filter(source_detail__load_source=handler).count()
        match_cnt = SourceDetailMatch.objects.filter(source_detail__load_source=handler).count()
        self.assertEquals(league_cnt, 2)
        self.assertEquals(match_cnt, 3)
        ## 2 - start_load
        handler.start_load()
        league_cnt = SourceDetailLeague.objects.filter(source_detail__load_source=handler).count()
        match_cnt = SourceDetailMatch.objects.filter(source_detail__load_source=handler).count()
        self.assertEquals(league_cnt, 0)
        self.assertEquals(match_cnt, 0)

    #######################################################################
    def test_common_handler_set_load_date(self):
        handler = self.handler
        detail_slug = 'set_load_date_detail'
        result = handler.start_load()
        self.assertTrue(result)
        self.assertEquals(handler.get_load_date(), date(2010, 1, 1))
        self.assertIsNone(handler.load_date)
        handler.start_detail(detail_slug)
        self.assertIsNone(handler.source_detail.load_date)
        #
        handler.set_load_date(date(2012, 2, 2))
        self.assertEquals(handler.get_load_date(), date(2012, 2, 2))
        self.assertEquals(handler.source_detail.load_date, date(2012, 2, 2))
        self.assertIsNone(handler.load_date)
        #
        handler.finish_detail()
        handler.set_load_date(date(2013, 3, 3))
        self.assertEquals(handler.get_load_date(), date(2013, 3, 3))
        self.assertEquals(handler.load_date, date(2013, 3, 3))
        #
        handler.start_detail(detail_slug)
        self.assertEquals(handler.get_load_date(), date(2012, 2, 2))

    #######################################################################
    def test_common_handler_start_or_skip_league(self):
        handler = self.handler
        detail_slug = 'start_or_skip_league_detail'
        league_name = 'start_or_skip_league_1'
        result = handler.start_load()
        self.assertTrue(result)
        handler.start_detail(detail_slug)
        do = handler.start_or_skip_league(league_name)
        self.assertTrue(do)
        self.assertIsNotNone(handler.source_detail_league)
        self.assertEquals(handler.source_detail_league.status, SourceDetail.IN_PROCESS)
        source_detail_league = handler.source_detail_league
        #restart load league
        do = handler.start_or_skip_league(league_name)
        self.assertTrue(do)
        #finish league
        handler.finish_league()
        self.assertIsNone(handler.source_detail_league)
        source_detail_league.refresh_from_db()
        self.assertEquals(source_detail_league.status, SourceDetail.FINISHED)
        do = handler.start_or_skip_league(league_name)
        self.assertFalse(do)
        #restart load
        handler.finish_load()
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        do = handler.start_or_skip_league(league_name)
        self.assertTrue(do)

    #######################################################################
    def test_common_handler_start_or_skip_match(self):
        handler = self.handler
        detail_slug = 'start_or_skip_league_detail'
        league_name = 'start_or_skip_league_1'
        name_h = 'start_or_skip_match_team_h'
        name_a = 'start_or_skip_match_team_a'
        match_date = date(2018,2,1)
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        handler.set_load_date(match_date)
        self.assertEquals(handler.match_date, match_date)
        do = handler.start_or_skip_league(league_name)
        self.assertTrue(do)
        do = handler.start_or_skip_match(name_h, name_a)
        self.assertTrue(do)
        self.assertIsNotNone(handler.source_detail_match)
        self.assertEquals(handler.source_detail_match.status, SourceDetail.IN_PROCESS)
        source_detail_match = handler.source_detail_match
        self.assertEquals(handler.name_h, name_h)
        self.assertEquals(handler.name_a, name_a)
        
        #restart load match
        do = handler.start_or_skip_match(name_h, name_a)
        self.assertTrue(do)
        #finish league
        handler.finish_match()
        self.assertIsNone(handler.source_detail_match)
        source_detail_match.refresh_from_db()
        self.assertEquals(source_detail_match.status, SourceDetail.FINISHED)
        do = handler.start_or_skip_match(name_h, name_a)
        self.assertFalse(do)
        
        #restart load
        handler.finish_load()
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        do = handler.start_or_skip_match(name_h, name_a, match_date=match_date)
        self.assertTrue(do)
        
        #delete team
        handler.team_h.delete_object()
        handler.finish_load()
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        do = handler.start_or_skip_match(name_h, name_a, match_date=match_date)
        self.assertFalse(do)

    #######################################################################
    def test_common_handler_save_match_stat(self):
        handler1 = CommonHandler.objects.get(slug=CommonHandler.SRC_ESPN)
        handler2 = CommonHandler.objects.get(slug=CommonHandler.SRC_UNDERSTAT)
        handler3 = CommonHandler.objects.get(slug=CommonHandler.SRC_FOOTBALL_DATA)
        detail_slug = 'match_stat_league_detail'
        league_name = 'match_stat_league_1'
        name_h = 'match_stat_team_h'
        name_a = 'match_stat_team_a'
        match_date = date(2018,3,1)
        team_h = Team.get_or_create(
            name=name_h, 
            team_type=self.team_type, sport=self.sport, load_source=handler3)
        team_h.confirm(handler3)
        self.assertEquals(team_h.load_source, handler3)
        self.assertEquals(team_h.slug, name_h)
        team_a = Team.get_or_create(
            name=name_a, 
            team_type=self.team_type, sport=self.sport, load_source=handler3)
        team_a.confirm(handler3)
        league = League.get_or_create(
                    name=league_name,
                    sport=self.football,
                    load_source=handler3)
        league.confirm(handler3)

        #prepare handler3
        self.assertTrue(handler3.start_load(detail_slug))
        handler3.set_load_date(match_date)
        self.assertTrue(handler3.start_or_skip_league(league_name))
        self.assertEquals(handler3.league, league)
        self.assertTrue(handler3.start_or_skip_match(name_h, name_a))
        self.assertEquals(handler3.source_detail_match.status, SourceDetail.IN_PROCESS)
        team_h = handler3.team_h
        team_a = handler3.team_a
        match = handler3.match
        #add football stats
        handler3.h.set_stats(goals=2, goals_1st=2, goals_2nd=0, possession=47)
        handler3.a.set_stats(goals=3, goals_1st=1, goals_2nd=2, possession=53)
        #save data and checks
        handler3.finish_match()
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '2')
        match.refresh_from_db()
        self.assertEquals(match.score, '2:3 (2:1,0:2)')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_HOME,period=15)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_AWAY,period=30)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '47')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '53')

        #prepare handler2
        handler3.finish_load()
        self.assertTrue(handler2.start_load(detail_slug))
        handler2.set_load_date(match_date)
        self.assertTrue(handler2.start_or_skip_league(league_name))
        self.assertTrue(handler2.start_or_skip_match(name_h, name_a))
        self.assertEquals(handler2.source_detail_match.status, SourceDetail.IN_PROCESS)
        team_h.refresh_from_db()
        self.assertEquals(handler2.team_h, team_h)
        self.assertEquals(handler2.team_a, team_a)
        self.assertEquals(handler2.match, match)
        #add football stats
        handler2.h.set_stats(
                        goals=0, xG=0, y_cards=0, r_cards=0, penalties=0,
                        goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0,
                        goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0,
                        init_goals_minutes=True, init_y_cards_minutes=True, init_r_cards_minutes=True,
                        init_goals_times=True,
                        shots=10, shots_on_target=2,
                        fouls=15, corners=5)
        handler2.a.set_stats(
                        goals=0, xG=0, y_cards=0, r_cards=0, penalties=0,
                        goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0, xG_1st=0,
                        goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0, xG_2nd=0,
                        init_goals_minutes=True, init_y_cards_minutes=True, init_r_cards_minutes=True,
                        init_goals_times=True,
                        shots=12, shots_on_target=5,
                        fouls=8, corners=9)
        handler2.h.add_event(12, goals=1)
        handler2.h.add_event(46, goals=1)
        handler2.h.add_event(47, goals=1)
        handler2.h.add_event(50, y_cards=1)
        handler2.h.add_event(81, y_cards=1)
        handler2.h.add_event(82, y_cards=1)
        handler2.h.add_event(90, r_cards=1)
        handler2.h.add_event(20, xG=0.2)
        handler2.h.add_event(30, xG=0.1)
        handler2.h.add_event(45, xG=0.8)
        handler2.a.add_event(40, goals=1)
        handler2.a.add_event(61, goals=1)
        handler2.a.add_event(61, goals=1)
        handler2.a.add_event(62, goals=1)
        handler2.a.add_event(12, y_cards=1)
        handler2.a.add_event(90, penalties=1)
        handler2.a.add_event(46, xG=0.5)
        handler2.a.add_event(80, xG=0.7)

        #save data and checks
        handler2.finish_match()
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.load_source, handler2)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '4')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '3')
        match.refresh_from_db()
        self.assertEquals(match.score, '3:4 (1:1,2:3)')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '1.1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1.2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '1.1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_HOME,period=15)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_AWAY,period=75)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG_MINUTE,competitor=Match.COMPETITOR_HOME,period=30)
        self.assertEquals(stat.value, '0.3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG_MINUTE,competitor=Match.COMPETITOR_AWAY,period=90)
        self.assertEquals(stat.value, '0.7')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '12,46,47')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '40,61,61,62')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '10')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '12')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '5')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '5')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '9')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '15')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '8')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '47')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '53')

        #prepare handler1
        handler2.finish_load()
        self.assertTrue(handler1.start_load(detail_slug))
        handler1.set_load_date(match_date)
        self.assertTrue(handler1.start_or_skip_league(league_name,country=self.russia))
        self.assertNotEquals(handler1.league, league)
        self.assertTrue(handler1.start_or_skip_match(name_h, name_a))
        self.assertNotEquals(handler1.team_h, team_h)
        self.assertNotEquals(handler1.team_a, team_a)
        self.assertEquals(handler1.source_detail_match.status, SourceDetail.IN_PROCESS)
        league1 = handler1.league
        team1_h = handler1.team_h
        team1_a = handler1.team_a
        match1 = handler1.match
        #add football stats
        handler1.h.set_stats(goals=5, goals_1st=3, goals_2nd=2, possession=41)
        handler1.a.set_stats(goals=7, goals_1st=4, goals_2nd=3, possession=59)
        #save data and merge
        handler1.finish_match()
        league1.merge_to(league)
        team1_h.merge_to(team_h)
        team1_a.merge_to(team_a)
        #checks
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.load_source, handler1)
        self.assertEquals(stat.value, '5')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '7')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '4')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '3')
        match.refresh_from_db()
        self.assertEquals(match.score, '5:7 (3:4,2:3)')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.load_source, handler2)
        self.assertEquals(stat.value, '1.1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1.2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '1.1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_HOME,period=1)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.YCARD,competitor=Match.COMPETITOR_AWAY,period=1)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.RCARD,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_HOME,period=2)
        self.assertEquals(stat.value, '0')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PENALTY,competitor=Match.COMPETITOR_AWAY,period=2)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_HOME,period=15)
        self.assertEquals(stat.value, '1')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOALS_MINUTE,competitor=Match.COMPETITOR_AWAY,period=75)
        self.assertEquals(stat.value, '3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG_MINUTE,competitor=Match.COMPETITOR_HOME,period=30)
        self.assertEquals(stat.value, '0.3')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.XG_MINUTE,competitor=Match.COMPETITOR_AWAY,period=90)
        self.assertEquals(stat.value, '0.7')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '12,46,47')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.GOAL_TIME,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '40,61,61,62')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '10')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '12')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '2')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.SHOTS_ON_TARGET,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '5')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.DEEP,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.PPDA,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '5')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.CORNERS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '9')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '15')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.FOULS,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '8')
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.OFFSIDES,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertIsNone(stat)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_HOME,period=0)
        self.assertEquals(stat.value, '41')
        self.assertEquals(stat.load_source, handler1)
        stat = MatchStats.get_object(match=match,stat_type=MatchStats.POSSESSION,competitor=Match.COMPETITOR_AWAY,period=0)
        self.assertEquals(stat.value, '59')




