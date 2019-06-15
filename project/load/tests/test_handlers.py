import os
from datetime import datetime, date, timedelta

from unittest import skip

from django.test import TestCase

from core.models import League, Team, Match, MatchStats
from load.handlers.espn import ESPNHandler


def prepare_data(obj):
    obj.handler = ESPNHandler.get()


#######################################################################################
######  ESPNHandler
#######################################################################################
class ESPNHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_espn_handler_get(self):
        handler = ESPNHandler.get()
        self.assertEquals(handler.slug, ESPNHandler.SRC_ESPN)


    #######################################################################
    def test_espn_process_degug_file(self):
        self.handler.process(is_debug=True)
        premier_league = League.objects.get(name= 'English Premier League', load_source=self.handler)
        self.assertEquals(premier_league.name, 'English Premier League')
        self.assertEquals(premier_league.country.slug, 'eng')
        season = premier_league.get_season(date(2019,2,2))
        self.assertEquals(season.start_date, date(2018,8,10))


    #######################################################################
    @skip("Skip load html")
    def test_espn_get_html(self):
        url = 'https://www.espn.com/soccer/scoreboard/_/league/all/date/20180202'
        file_name = 'test.html'
        html1 = self.handler.get_html(file_name, url=url)

        fname = self.handler.get_handler_dir().path('cache').path(file_name)
        html2 = open(fname, 'rb').read()
        self.assertEquals(html1.encode(), html2)

        html3 = self.handler.get_html('test.html', get_from_file=True, is_debug_path=False)
        self.assertEquals(html1.encode(), html3)

        os.remove(fname)