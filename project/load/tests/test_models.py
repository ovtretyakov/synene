from datetime import datetime, date, timedelta

from django.test import TestCase
from django.utils import timezone

from load.models import (
                        CommonHandler, 
                        SourceSession, 
                        SourceDetail, 
                        ErrorLog,
                        SourceDetailLeague,
                        SourceDetailMatch)
from load.exceptions import LoadError


def prepare_data(obj):
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
        self.assertIsNone(handler.source_detail)
        handler.start_detail(detail_slug)
        self.assertEquals(handler.source_detail.status, SourceDetail.IN_PROCESS)
        self.assertEquals(handler.source_detail.pk, source_detail_pk)
        start_load = handler.start_or_skip_league('common_handler_details_league 1')
        start_load = handler.start_or_skip_league('common_handler_details_league 2')
        start_load = handler.start_or_skip_match(date(2018,1,1), 'common_handler_details_match 1')
        start_load = handler.start_or_skip_match(date(2018,1,1), 'common_handler_details_match 2')
        start_load = handler.start_or_skip_match(date(2018,1,1), 'common_handler_details_match 3')
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
        match_name = 'start_or_skip_match_1'
        match_date = date(2018,2,1)
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        do = handler.start_or_skip_league(league_name)
        self.assertTrue(do)
        do = handler.start_or_skip_match(match_date, match_name)
        self.assertTrue(do)
        self.assertIsNotNone(handler.source_detail_match)
        self.assertEquals(handler.source_detail_match.status, SourceDetail.IN_PROCESS)
        source_detail_match = handler.source_detail_match
        #restart load match
        do = handler.start_or_skip_match(match_date, match_name)
        self.assertTrue(do)
        #finish league
        handler.finish_match()
        self.assertIsNone(handler.source_detail_match)
        source_detail_match.refresh_from_db()
        self.assertEquals(source_detail_match.status, SourceDetail.FINISHED)
        do = handler.start_or_skip_match(match_date, match_name)
        self.assertFalse(do)
        #restart load
        handler.finish_load()
        result = handler.start_load(detail_slug)
        self.assertTrue(result)
        do = handler.start_or_skip_match(match_date, match_name)
        self.assertTrue(do)

