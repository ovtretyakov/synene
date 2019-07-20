import os
from datetime import datetime, date, timedelta
import logging
import csv
import re
from decimal import Decimal

from bs4 import BeautifulSoup
from urllib.request import urljoin

from django.utils import timezone

from core.models import Country
from load.models import CommonHandler
from betting.models import BetType
from load.exceptions import TooMamyErrors

logger = logging.getLogger(__name__)




###################################################################
class FootballDataHandler(CommonHandler):

    DEBUG_DATE = date(1900, 1, 1)
    main_file   = 'football-data.html'
    league_file = 'football-data_league_%s.html'
    data_file   = 'football-data_%s_%s_%s.csv'

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_FOOTBALL_DATA)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path('football_data') 


    def process(self, debug_level=0, get_from_file=False, is_debug_path=True, start_date=None):
        source_session = None
        try:
            source_session = self.start_load(is_debug=debug_level)

            main_url = 'http://www.football-data.co.uk/data.php'
            html = self.get_html(self.main_file, main_url, get_from_file, is_debug_path)
            self.context = html

            soup = BeautifulSoup(html, 'html.parser')
            main_leagues_p = soup.find('b', string='Main Leagues').parent

            main_leagues_table = main_leagues_p.find_next_sibling('table')
            extra_leagues_table = main_leagues_table.find_next_sibling('table')
            leagues = main_leagues_table.find_all('tr') + extra_leagues_table.find_all('tr')
            # for row in main_leagues_table.find_all('tr'):
            for league in leagues:
                self.context = html
                league_a = league.select('td:nth-child(2) > a')[0]
                league_name  = league_a.get_text()
                country_name = league_name.split()[0]
                league_href = league_a['href']
                if not league_href.startswith('http'): league_href = urljoin(main_url, league_href)
                self.process_country_league(country_name, league_href, 
                                            debug_level, get_from_file, is_debug_path, 
                                            start_date)
                if debug_level == 2:
                    break

        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()
        return source_session



    def process_country_league(self, country_name, country_url, 
                                debug_level=0, get_from_file=False, is_debug_path=True,
                                init_start_date=None):
        ''' Process all country leagues 
            Site http://www.football-data.co.uk

            Arguments:
            country_name - country name (England)
            country_url  - URL (http://www.football-data.co.uk/englandm.php)

        '''
        file_name = self.league_file % country_name
        html = self.get_html(file_name, country_url, get_from_file, is_debug_path)
        self.context = html

        try:
            country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            country = Country.get_object('na')

        if init_start_date:
            start_date = init_start_date
        else:
            start_date = self.get_load_date()
        if start_date.month <= 6:
            start_year = start_date.year-1
        else:
            start_year = start_date.year
        logger.info('Start date: %s, Start year: %s' % (start_date, start_year))

        soup = BeautifulSoup(html, 'html.parser')
        pattern = re.compile(r'(\d+)/')   #<i>Season 1993/1994</i>

        # <i>Season 2000/2001</i>
        seasons = soup.find_all('i', string=re.compile('Season'))
        if seasons:
            for season in sorted(seasons, key=str):
                self.context = season
                start_season_year_str = int(pattern.search(season.string)[1])
                start_season_year = int(start_season_year_str)
                season_name = season.get_text().strip()
                if start_season_year >= start_year :
                    for tag in season.find_next_siblings(['a','i']):
                        if tag.name == 'i':
                            # found tag i - start next season
                            if debug_level:
                                break
                        elif tag.name == 'a':
                            #<a href="mmz4281/9798/E0.csv">Premier League</a>
                            league_name = str(tag.string)
                            league_href = tag['href']
                            if not league_href.startswith('http'): league_href = urljoin(country_url, league_href)
                            if league_href.find('csv') < 0:
                                #not csv file - exit from for
                                break
                        self.process_league(country, country_name, league_name, league_href, start_date, 
                                        start_season_year_str, 
                                        debug_level=debug_level, get_from_file=get_from_file, is_debug_path=is_debug_path)
                        if debug_level >= 2:
                            break
        else:
            CSV = soup.find('a', string='CSV')
            self.context = CSV
            league_name = ''
            league_href = CSV['href']
            if not league_href.startswith('http'): league_href = urljoin(country_url, league_href)
            self.process_league(country, country_name, league_name, league_href, start_date=start_date, 
                            debug_level=debug_level, get_from_file=get_from_file, is_debug_path=is_debug_path)


    def process_league(self, country, country_name, league_name, league_url, start_date, start_year='', 
                        debug_level=0, get_from_file=False, is_debug_path=True):
        ''' Process single league
            Site http://www.football-data.co.uk

            Arguments:
            country_name - league name (England)
            league_name  - league name (Premier League)
            start_year  -  start year of season (2018)
            league_url   - URL csv-file (http://www.football-data.co.uk/mmz4281/0001/E0.csv)

        '''

        file_name = self.data_file % (country_name, league_name, start_year)
        html = self.get_html(file_name, league_url, get_from_file, is_debug_path)
        reader = csv.DictReader(html.decode().splitlines())

        if league_name:
            if not self.start_or_skip_league(country_name + ' ' + league_name, country=country, detail_slug=league_name):
                return
        else:
            self.start_detail(country_name) 
        last_date = None
        for row in reader:
            self.context = row

            try:
                league_name, last_date = self.process_match(country, country_name, league_name, start_date, row)
            except TooMamyErrors:
                raise
            except Exception as e:
                self.handle_exception(e)
            finally:
                self.context = None

        if last_date:
            self.set_load_date(last_date)
        self.finish_league() 
        self.finish_detail() 


    def process_match(self, country, country_name, league_name, start_date, match_data):
        ''' Process single match
            Site http://www.football-data.co.uk

            Arguments:
            league
            match_data
        '''

        #date
        match_date_str = match_data['Date']
        if len(match_date_str) == 8:
            match_date=datetime.strptime(match_date_str, "%d/%m/%y").date()
        elif len(match_date_str) == 10:
            match_date=datetime.strptime(match_date_str, "%d/%m/%Y").date()
        else:
            raise ValueError('Empty match date')
        if match_date < start_date:
            return league_name, None


        row_league_name = match_data.get('League', '')
        if row_league_name:
            if league_name:
                #check - if league_name changed
                if row_league_name != league_name:
                    self.finish_league()
                    if not self.start_or_skip_league(country_name + ' ' + row_league_name, country=country):
                        return row_league_name, None
            else:
                if not self.start_or_skip_league(country_name + ' ' + row_league_name, country=country):
                    return row_league_name, None
            league_name = row_league_name
        else:
            #setting load date only for main league_name
            #for others - at the end of file
            self.set_load_date(match_date)

        #Home/Away teams
        try:
            home_team = match_data['HomeTeam']
        except KeyError:
            home_team = match_data['Home']
        try:
            away_team = match_data['AwayTeam']
        except KeyError:
            away_team = match_data['Away']


        #h_goals
        try:
            h_goals = match_data['FTHG']
        except KeyError:
            h_goals = match_data['HG']
        if h_goals == '': h_goals = None
        if not h_goals == None: h_goals = int(h_goals)
        #a_goals
        try:
            a_goals = match_data['FTAG']
        except KeyError:
            a_goals = match_data['AG']
        if a_goals == '': a_goals = None
        if not a_goals == None: a_goals = int(a_goals)

        #h_goals_1st
        h_goals_1st = match_data.get('HTHG',None)
        if not h_goals_1st == None: h_goals_1st = int(h_goals_1st)
        #a_goals_1st
        a_goals_1st = match_data.get('HTAG')
        if a_goals_1st: a_goals_1st = int(a_goals_1st)
        #h_goals_2nd
        if h_goals_1st != None and h_goals != None:
            h_goals_2nd = h_goals - h_goals_1st
        else:
            h_goals_2nd = None
        #a_goals_2nd
        if a_goals_1st != None and a_goals != None:
            a_goals_2nd = a_goals - a_goals_1st
        else:
            a_goals_2nd = None
        #shots
        h_shots = match_data.get('HS', None)
        a_shots = match_data.get('AS', None)
        #shots_on_target
        h_shots_on_target = match_data.get('HST', None)
        a_shots_on_target = match_data.get('AST', None)
        #corners
        h_corners = match_data.get('HC', None)
        a_corners = match_data.get('AC', None)
        #fouls
        h_fouls = match_data.get('HF', None)
        a_fouls = match_data.get('AF', None)
        #free_kicks
        h_free_kicks = match_data.get('HFKC', None)
        a_free_kicks = match_data.get('AFKC', None)
        #offsides
        h_offsides = match_data.get('HO', None)
        a_offsides = match_data.get('AO', None)
        #Yellow Cards
        h_y_cards = match_data.get('HY', None)
        a_y_cards = match_data.get('AY', None)
        #Red Cards
        h_r_cards = match_data.get('HR', None)
        a_r_cards = match_data.get('AR', None)

        if not self.start_or_skip_match(
                            home_team, away_team,
                            match_date=match_date,
                            referee=match_data.get('Referee',None)
                            ):
            return league_name, match_data


        self.h.set_stats(
                        goals=h_goals, goals_1st=h_goals_1st, goals_2nd=h_goals_2nd,
                        shots = h_shots if h_shots == None else int(h_shots),
                        shots_on_target = h_shots_on_target if h_shots_on_target == None else int(h_shots_on_target),
                        corners = h_corners if h_corners == None else int(h_corners),
                        fouls = h_fouls if h_fouls == None else int(h_fouls),
                        free_kicks = h_free_kicks if h_free_kicks == None else int(h_free_kicks),
                        offsides = h_offsides if h_offsides == None else int(h_offsides),
                        y_cards = h_y_cards if h_y_cards == None else int(h_y_cards),
                        r_cards = h_r_cards if h_r_cards == None else int(h_r_cards)
                        )
        self.a.set_stats(
                        goals=a_goals, goals_1st=a_goals_1st, goals_2nd=a_goals_2nd,
                        shots = a_shots if a_shots == None else int(a_shots),
                        shots_on_target = a_shots_on_target if a_shots_on_target == None else int(a_shots_on_target),
                        corners = a_corners if a_corners == None else int(a_corners),
                        fouls = a_fouls if a_fouls == None else int(a_fouls),
                        free_kicks = a_free_kicks if a_free_kicks == None else int(a_free_kicks),
                        offsides = a_offsides if a_offsides == None else int(a_offsides),
                        y_cards = a_y_cards if a_y_cards == None else int(a_y_cards),
                        r_cards = a_r_cards if a_r_cards == None else int(a_r_cards)
                        )
        #avarage 1x0
        win = match_data.get('PH', None)
        if not win: win = match_data.get('PSH', None)
        if not win: win = match_data.get('B365H', None)
        if not win: win = match_data.get('LBH', None)
        if not win: win = match_data.get('WHH', None)
        if not win: win = match_data.get('BbAvH', None)
        if not win: win = match_data.get('AvgH', None)
        if win:
            self.odds.append({'bet_type':BetType.WDL, 'odd_value':win, 'param':'w'})
        draw = match_data.get('PSD', None)
        if not draw: draw = match_data.get('PD', None)
        if not draw: draw = match_data.get('B365D', None)
        if not draw: draw = match_data.get('LBD', None)
        if not draw: draw = match_data.get('WHD', None)
        if not draw: draw = match_data.get('BbAvD', None)
        if not draw: draw = match_data.get('AvgD', None)
        if draw:
            self.odds.append({'bet_type':BetType.WDL, 'odd_value':draw, 'param':'d'})
        lose = match_data.get('PSA', None)
        if not lose: lose = match_data.get('PA', None)
        if not lose: lose = match_data.get('B365A', None)
        if not lose: lose = match_data.get('LBA', None)
        if not lose: lose = match_data.get('WHA', None)
        if not lose: lose = match_data.get('BbAvA', None)
        if not lose: lose = match_data.get('AvgA', None)
        if lose:
            self.odds.append({'bet_type':BetType.WDL, 'odd_value':lose, 'param':'l'})

        #totals
        over = match_data.get('B365>2.5', None)
        if not over: over = match_data.get('GB>2.5', None)
        if not over: over = match_data.get('BbAv>2.5', None)
        if over:
            self.odds.append({'bet_type':BetType.TOTAL_OVER, 'odd_value':over, 'param':'2.5'})
        under = match_data.get('B365<2.5', None)
        if not under: under = match_data.get('GB<2.5', None)
        if not under: under = match_data.get('BbAv<2.5', None)
        if under:
            self.odds.append({'bet_type':BetType.TOTAL_UNDER, 'odd_value':under, 'param':'2.5'})

        #Asian handicap
        handicap_h = None
        handicap_a = None
        if match_data.get('B365AH', None):
            handicap_param = match_data.get('B365AH', None)
            handicap_h = match_data.get('B365AHH', None)
            handicap_a = match_data.get('B365AHA', None)
        elif match_data.get('LBAH', None):
            handicap_param = match_data.get('LBAH', None)
            handicap_h = match_data.get('LBAHH', None)
            handicap_a = match_data.get('LBAHA', None)
        elif match_data.get('BbAHh', None):
            handicap_param = match_data.get('BbAHh', None)
            handicap_h = match_data.get('BbAvAHH', None)
            handicap_a = match_data.get('BbAvAHA', None)

        if handicap_h:
            self.odds.append(
                    {
                        'bet_type':BetType.HANDICAP, 
                        'team':'h',
                        'odd_value':handicap_h, 
                        'param':handicap_param
                    })
        if handicap_a:
            param = Decimal(handicap_param)
            param = '0' if param==0 else str(-1*param)
            self.odds.append(
                    {
                        'bet_type':BetType.HANDICAP, 
                        'team':'a',
                        'odd_value':handicap_a, 
                        'param':param
                    })

        self.finish_match()
        return league_name, match_date

