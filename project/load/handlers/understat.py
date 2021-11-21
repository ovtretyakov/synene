import os
import re
from datetime import datetime, date, timedelta
import logging
import json

from bs4 import BeautifulSoup
from urllib.request import urljoin

from django.utils import timezone

from ..models import CommonHandler
from ..exceptions import TooMamyErrors

logger = logging.getLogger(__name__)




###################################################################
class UnderstatHandler(CommonHandler):

    DEBUG_DATE = date(2018, 8, 11)
    main_file   = 'understat.html'
    league_file = 'understat_league_%s.html'
    league_year_file = 'understat_league_year_%s_%s.html'
    match_file  = 'understat_match_%s_%s_%s.html'

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_UNDERSTAT)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path('understat') 




    def process(self, debug_level=0, get_from_file=False, is_debug_path=True, start_date=None, number_of_days=10):
        ''' Process all leagues
            Site https://understat.com/

        '''
        source_session = None
        try:
            source_session = self.start_load(is_debug=debug_level)

            main_url = 'https://understat.com/'
            html = self.get_html(self.main_file, main_url, get_from_file, is_debug_path)
            self.context = html

            soup = BeautifulSoup(html, 'html.parser')

            #select all leagues
            load_date = None
            for league in soup.select('nav.m-navigation > ul > li > a'):
                self.context = league
                league_name = league.get_text().strip()
                league_href = league['href']
                if not league_href.startswith('http'): 
                    league_href = urljoin(main_url, league_href)
                
                try:
                    if not self.start_or_skip_league(league_name, detail_slug=league_name):
                        #skip league
                        continue

                    #process league
                    league_load_date = self.process_league(league_name, league_href, debug_level, get_from_file, 
                                                           is_debug_path, start_date, number_of_days
                                                           )
                    if not load_date or league_load_date < load_date:
                        load_date = league_load_date

                    self.finish_league()
                    self.finish_detail()
                except TooMamyErrors:
                    raise
                except Exception as e:
                    self.handle_exception(e)
                finally:
                    self.context = None
                    if debug_level >= 2: 
                        break
            if load_date:
                self.set_load_date(load_date=load_date, is_set_main=True)


        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()
        return source_session




    def process_league(self, league_name, league_url, 
                        debug_level=0, get_from_file=False, is_debug_path=True, 
                        init_start_date=None, number_of_days=10):
        ''' Process single league
            Site https://understat.com/

            Arguments:
            league_name - league name (EPL)
            league_url  - URL (https://understat.com/league/EPL)

        '''

        file_name = self.league_file % league_name
        html = self.get_html(file_name, league_url, get_from_file, is_debug_path)
        self.context = html

        soup = BeautifulSoup(html, 'html.parser')
      
        # #selected_league
        # selected_league = soup.select('select[name="league"] > option[selected]')[0]
        # print('--> league - %s' % (str(selected_league.string)))

        #select all seasons
        if init_start_date:
            start_date = init_start_date
        else:
            start_date = self.get_load_date()
        if start_date.month <= 6:
            start_year = start_date.year-1
        else:
            start_year = start_date.year
        finish_date = start_date + timedelta(days=number_of_days)
        finish_year = finish_date.year
        logger.info('Start date: %s, finish date: %s' % (start_date,finish_date))

        load_date = None
        for season in sorted(soup.select('select[name="season"] > option'), key=lambda x: x['value']):
            self.context = season
            season_name = season.get_text().strip()
            season_value = season['value']
            season_year = int(season_value)
            if int(season_value) >= start_year and int(season_value) <= finish_year:
                logger.debug('Process %s year %s' % (season_name, season_value))
                league_load_date = self.process_league_year(
                                        league_url, season_year, start_date, finish_date,
                                        debug_level, get_from_file, is_debug_path)
                logger.info('Leageu load date: %s' % league_load_date)
                if league_load_date:
                    load_date = league_load_date
                if debug_level >= 1: 
                    break
        logger.info('Load date: %s' % load_date)
        return load_date


    def process_league_year(self, league_url, season_year, start_date, finish_date,
                            debug_level=0, get_from_file=False, is_debug_path=True):
        ''' Process single league year
            Site https://understat.com/

            Arguments:
            league_url  - URL (https://understat.com/league/EPL)
            season_year - year (2016)

        '''
        year_url = league_url + '/' + str(season_year)

        file_name = self.league_year_file % (self.league_name, season_year)
        html = self.get_html(file_name, year_url, get_from_file, is_debug_path)
        self.context = html

        soup = BeautifulSoup(html, 'html.parser')
        datesData_pattern = re.compile(r"JSON\.parse\('([^')]+)")   #JSON.parse('...')

        #find script with "datesData"
        script = soup.find('script', string=re.compile("datesData"))

        datesData = (datesData_pattern.search(script.string)[1]).encode('utf8').decode('unicode_escape')
        matches = json.loads(datesData)
        i = 0
        load_date = None
        for match in matches:
            self.context = match
            i += 1

            try:
                match_date_str = match['datetime'][:10]
                match_date = datetime.strptime(match_date_str, "%Y-%m-%d").date()
                if match_date < start_date:
                    continue
                elif debug_level == 1 and match_date > start_date: 
                    break
                if match_date > finish_date:
                    break

                self.set_load_date(match_date)
                if self.process_match(match, debug_level, get_from_file, is_debug_path, match_date_str):
                    load_date = match_date
            except TooMamyErrors:
                raise
            except Exception as e:
                self.handle_exception(e)
            finally:
                self.context = None
                if debug_level >= 2: 
                    break
        return load_date


    def process_match(self, match_data, debug_level=0, get_from_file=False, is_debug_path=True, match_date_str=None):
        ''' Process single match
            Site https://understat.com/

            Arguments:
            match_data - format match data:
                        "id":"461","isResult":true
                        "h":{"id":"91","title":"Hull","short_title":"HUL"},
                        "a":{"id":"75","title":"Leicester","short_title":"LEI"},
                        "goals":{"h":"2","a":"1"},
                        "xG":{"h":"0.740018","a":"2.45631"},
                        "datetime":"2016-08-13 15:30:00",
                        "forecast":{"w":"0.0538","d":"0.1247","l":"0.8215"}
        '''
  
        # prepare match_detail
        if not match_data['isResult']:
            return False
        match_id = match_data['id']
        team     = match_data['h']
        name_h   = team['title']
        team     = match_data['a']
        name_a   = team['title']
        forecast = match_data['forecast']

        if self.start_or_skip_match(name_h, name_a,
                                    forecast_w=float(forecast['w']), 
                                    forecast_d=float(forecast['d']), 
                                    forecast_l=float(forecast['l'])
                                    ):

            self.h.set_stats(
                                goals=0, y_cards=0, r_cards=0, penalties=0,
                                goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0,
                                goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0,
                                init_goals_minutes=True, init_xG_minutes=True, 
                                init_y_cards_minutes=True, init_r_cards_minutes=True, 
                                init_goals_times=True,
                                shots=0, shots_on_target=0, deep=0, ppda=0)
            self.a.set_stats(
                                goals=0, y_cards=0, r_cards=0, penalties=0,
                                goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0,
                                goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0,
                                init_goals_minutes=True, init_xG_minutes=True, 
                                init_y_cards_minutes=True,init_r_cards_minutes=True, 
                                init_goals_times=True,
                                shots=0, shots_on_target=0, deep=0, ppda=0)
            #Get match detail
            match_url = 'https://understat.com/match/' + match_id

            file_name = self.match_file % (name_h, name_a, match_date_str)
            html = self.get_html(file_name, match_url, get_from_file, is_debug_path)

            self.process_match_html(html)

            self.finish_match()
        return True


    def process_match_html(self, html):
        self.context = html

        soup = BeautifulSoup(html, 'html.parser')
        shotsData_pattern   = re.compile(r"shotsData[^\(]*\('([^')]+)")     #shotsData...('...')
        match_info_pattern  = re.compile(r"match_info[^\(]*\('([^')]+)")    #match_info...('...')

        script  = soup.find('script', string=re.compile("shotsData"))
        self.context = script

        #process shotsData
        #{"h":[{"id":"112236",
        #         "minute":"5",
        #         "result":"MissedShots",
        #         "X":"0.9159999847412109",
        #         "Y":"0.585",
        #         "xG":"0.01687188446521759",
        #         "player":"Curtis Davies",
        #         "h_a":"h",
        #         "player_id":"1686",
        #         "situation":"FromCorner",
        #         "season":"2016",
        #         "shotType":"Head",
        #         "match_id":"461",
        #         "h_team":"Hull",
        #         "a_team":"Leicester",
        #         "h_goals":"2",
        #         "a_goals":"1",
        #         "date":"2016-08-13 15:30:00",
        #         "player_assisted":"Robert Snodgrass",
        #         "lastAction":"Aerial"
        #         },...
        #       ],
        #   "a":[{},...]
        # }

        shotsData  = json.loads((shotsData_pattern.search(script.string)[1]).encode('utf8').decode('unicode_escape'))
        events = shotsData['h']
        for event in events:
            self.context = event
            minute = int(event['minute'])
            xG = float(event['xG'])
            self.h.add_event(minute, xG=xG)
        self.context = script

        events = shotsData['a']
        for event in events:
            self.context = event
            minute = int(event['minute'])
            xG = float(event['xG'])
            self.a.add_event(minute, xG=xG)
        self.context = script


        #process match_info
        # {"id":"461","fid":"1080512","h":"91","a":"75","date":"2016-08-13 15:30:00",
        #  "league_id":"1","season":"2016",
        #  "h_goals":"2","a_goals":"1",
        #  "team_h":"Hull","team_a":"Leicester",
        #  "h_xg":"0.740018","a_xg":"2.45631",
        #  "h_w":"0.0538","h_d":"0.1247","h_l":"0.8215",
        #  "league":"EPL",
        #  "h_shot":"14","a_shot":"18",
        #  "h_shotOnTarget":"5","a_shotOnTarget":"5",
        #  "h_deep":"0","a_deep":"5",
        #  "a_ppda":"11.2800","h_ppda":"17.8667"}  
        match_info = json.loads((match_info_pattern.search(script.string)[1]).encode('utf8').decode('unicode_escape'))
        self.context = match_info
        self.set_shots(h_shots=int(match_info['h_shot']), a_shots=int(match_info['a_shot']))
        self.set_shots_on_target(   h_shots_on_target=int(match_info['h_shotOnTarget']), 
                                    a_shots_on_target=int(match_info['a_shotOnTarget']))
        self.set_deep(h_deep=int(match_info['h_deep']), a_deep=int(match_info['a_deep']))
        self.set_ppda(h_ppda=float(match_info['h_ppda']), a_ppda=float(match_info['a_ppda']))

        #process goals and cards
        # <div class="timiline-block">
        #   <div class="timiline-container">
        #     <div class="timeline-left">
        #       <div class="timeline-block block-home"></div>
        #     </div>
        #     <div class="timeline-minute"><span class="minute-value">28'</span></div>
        #     <div class="timeline-right">
        #       <div class="timeline-block block-away">
        #         <div class="timeline-row">
        #           <i class="fas fa-square yellow-card" aria-hidden="true" title="Yellow card"></i>
        #           <a class="player-name" href="https://understat.com/player/749">Christian Fuchs</a>
        #         </div>
        #       </div>
        #     </div>
        #   </div>
        #   <div class="timiline-container">
        #     <div class="timeline-left">
        #       <div class="timeline-block block-home">
        #         <div class="timeline-row">
        #           <a class="player-name" href="https://understat.com/player/1694">Adama Diomande</a> <span class="match-score">1 - 0</span>
        #           <i class="fas fa-futbol" aria-hidden="true" title="Goal"></i>
        #         </div>
        #       </div>
        #     </div>
        #     <div class="timeline-minute"><span class="minute-value">45'</span></div>
        #     <div class="timeline-right"><div class="timeline-block block-away"></div></div>
        #   </div>
        #   ...
        # </div>
        self.context = html
        rows = soup.select('div.timiline-block > div.timiline-container')
        self.context = rows
        for row in rows:
            self.context = row
            span_minute = row.select('span.minute-value')[0]
            minute = int(span_minute.string[:-1])+1
            if minute > 90:
                minute = 90
            # home team
            left = row.select('div.timeline-left')[0]
            events = left.find_all('i')
            if events:
                for event in events:
                    self.context = event
                    if event['title'] == 'Yellow card':
                        self.h.add_event(minute, y_cards=1)
                    elif event['title'] == 'Red card':
                        self.h.add_event(minute, r_cards=1)
                    elif event['title'] == 'Goal':
                        self.h.add_event(minute, goals=1)
                    elif event['title'] == 'Penalty':
                        self.h.add_event(minute, goals=1, penalties=1)
                    elif event['title'] in('Own goal'):
                        self.a.add_event(minute, goals=1)
                self.context = row
            # against team
            right = row.select('div.timeline-right')[0]
            events = right.find_all('i')
            if events:
                for event in events:
                    self.context = event
                    if event['title'] == 'Yellow card':
                        self.a.add_event(minute, y_cards=1)
                    elif event['title'] == 'Red card':
                        self.a.add_event(minute, r_cards=1)
                    elif event['title'] == 'Goal':
                        self.a.add_event(minute, goals=1)
                    elif event['title'] == 'Penalty':
                        self.a.add_event(minute, goals=1, penalties=1)
                    elif event['title'] in('Own goal'):
                        self.h.add_event(minute, goals=1)
        self.context = None
