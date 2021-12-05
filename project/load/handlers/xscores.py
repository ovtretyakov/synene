import os
from datetime import datetime, date, timedelta
import logging
import csv
import re
from decimal import Decimal

from bs4 import BeautifulSoup
from urllib.request import urljoin

from django.utils import timezone

from project.core.models import Country, Match
from project.betting.models import BetType
from ..models import CommonHandler
from ..exceptions import TooMamyErrors

logger = logging.getLogger(__name__)




###################################################################
class XScoresHandler(CommonHandler):

    matches_file = 'xscore_%s.html'

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_XSCORES)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path('xscores') 


    def process(self, debug_level=0, get_from_file=False, is_debug_path=True, start_date=None, number_of_days=7):
        '''Main method to load site''' 

        source_session = None
        try:
            self.start_load('Main handler', is_debug=debug_level)
            source_session = self.source_session

            if debug_level and not start_date:
                get_from_file = True
            if start_date:
                dat = start_date
            else:
                dat = self.get_load_date()
            if number_of_days == None or number_of_days > 7 or number_of_days < 0:
                number_of_days = 7
            match5 = datetime.now().date() - timedelta(days=number_of_days)
            match7 = datetime.now().date() - timedelta(days=7)
            if dat < match5:
                dat = match7
            else:
                dat = match5
            last_date = timezone.now().date() + timedelta(days=2)
            logger.info('Start date: %s, finish date: %s' % (dat,last_date))
            while dat <= last_date:

                logger.info('Process date: %s' % dat)
                self.set_load_date(load_date=dat, is_set_main=True)
                self.process_date(dat, debug_level, get_from_file, is_debug_path)

                dat += timedelta(days=1)
                if debug_level: break
        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()
        return source_session



    def process_date(self, match_date, debug_level, get_from_file, is_debug_path):
        ''' Process single date
            Site https://www.xscores.com/soccer/livescores

            Arguments:
            match_date  - Date 
            debug_level    - is debugging

        '''
        file_name = self.matches_file % match_date.strftime('%d-%m')
        url = 'https://www.xscores.com/soccer/' + match_date.strftime('%d-%m')
        html = self.get_html(file_name, url, get_from_file, is_debug_path)
        self.context = html

        soup = BeautifulSoup(html, 'html.parser')
        referee_pattern = re.compile(r"Referee:([^.]*)")   #Referee: Stuart Attwell.



        matches = soup.select('div#scoretable > a.match_line')
        for match in matches:
            self.context = match
            finished = (match['data-game-status']=='Fin')
            country_name = match['data-country-name']
            try:
                country = Country.objects.get(name__iexact=country_name)
            except Country.DoesNotExist:
                country = Country.get_object('na')

            league_name  = match['data-league-name'].strip()
            round_name  = match['data-league-round']
            match_status = match['data-game-status']
            # data_note = match['data-note']
            # referee_match = referee_pattern.search(data_note) 
            # if referee_match:
            #     referee_name = referee_match[1].strip()
            # else:
            #     referee_name = None
            referee_name = None
            match_date = datetime.strptime(match['data-matchday'], '%Y-%m-%d').date()

            league_name = country.slug + ' ' + league_name
            logger.info('League: %s' % league_name)
            if not self.start_or_skip_league(league_name, country=country):
                continue

            score_teams = match.select('.score_teams')[0]
            home = score_teams.select('div.score_home')[0]
            away = score_teams.select('div.score_away')[0]
            name_h = (home.select('.score_home_txt')[0]).get_text().strip()
            name_a = (away.select('.score_away_txt')[0]).get_text().strip()
            logger.info('Match: %s%s' % (name_h,name_a))
            if not self.start_or_skip_match(name_h, name_a, referee=referee_name,
                                            match_status=Match.FINISHED if finished else Match.SCHEDULED):
                continue

            #Cards
            ycards_h = None
            ycards_a = None
            rcards_h = None
            rcards_a = None
            if finished:
                ycards_h = home.select('div.y_cards > span')
                ycards_a = away.select('div.y_cards > span')
                rcards_h = home.select('div.r_cards > span')
                rcards_a = away.select('div.r_cards > span')
                if ycards_h or ycards_a or rcards_h or rcards_a:
                    ycards_h = '0' if not ycards_h else ycards_h[0].get_text().strip()
                    ycards_a = '0' if not ycards_a else ycards_a[0].get_text().strip()
                    rcards_h = '0' if not rcards_h else rcards_h[0].get_text().strip()
                    rcards_a = '0' if not rcards_a else rcards_a[0].get_text().strip()
                else:
                    ycards_h = None
                    ycards_a = None
                    rcards_h = None
                    rcards_a = None

            #Goals
            goals_h     = None
            goals_a     = None
            goals_1st_h = None
            goals_1st_a = None
            goals_2nd_h = None
            goals_2nd_a = None
            if finished:
                goals_h     = int((match.select('div.scoreh_ft')[0]).get_text())
                goals_a     = int((match.select('div.scorea_ft')[0]).get_text())
                goals_1st_h = int((match.select('div.scoreh_ht')[0]).get_text())
                goals_1st_a = int((match.select('div.scorea_ht')[0]).get_text())
                goals_2nd_h = goals_h - goals_1st_h
                goals_2nd_a = goals_a - goals_1st_a

                self.set_y_cards(ycards_h, ycards_a)
                self.set_r_cards(rcards_h, rcards_a)
                self.set_goals(goals_h, goals_a)
                self.set_half_goals(1, goals_1st_h, goals_1st_a)
                self.set_half_goals(2, goals_2nd_h, goals_2nd_a)

            self.finish_match()

