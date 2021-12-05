import os
import time
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import logging

import requests
import re

from urllib.request import urljoin
from bs4 import BeautifulSoup, Comment, element
# from selenium import webdriver

from project.core.models import Match
from project.betting.models import ValueType, BetType
from ..models import CommonHandler
from ..exceptions import TooMamyErrors


logger = logging.getLogger(__name__)


XBET_VALUE_TYPES = {
          'main': ValueType.MAIN,
          'match_stat': ValueType.MAIN,
          'corn': ValueType.CORNER,
          'y_card': ValueType.Y_CARD,
          'r_card': ValueType.R_CARD,
          'fouls': ValueType.FOUL,
          'shots_on_goal': ValueType.SHOT_ON_GOAL,
          'shots_all': ValueType.SHOT,
          'offsides': ValueType.OFFSIDE,
          'ball_poss': ValueType.POSSESSION,
          'penalty': ValueType.PENALTY,
        }




###################################################################
class XBetHandler(CommonHandler):

    base_url    = 'https://1xstavka.ru/'
    test_dir    = 'test_files'
    load_dir    = 'load_files'

    main_file         = '1xbet_main_%s.html'
    league_file       = '1xbet_league_%s_%s.html'
    add_file          = '1xbet_add_%s-%s.json'
    add_stats_file    = '1xbet_add_stats_%s-%s.json'

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_1XBET)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path("1xbet") 


    def process(self, debug_level=0, get_from_file=False, is_debug_path=True, start_date=None, main_file=None):
        ''' Process site
            Site https://1xstavka.ru/line/Football/

            Arguments:
            debug_level
        '''
        source_session = None
        try:
            source_session = self.start_load(is_debug=debug_level)

            if not start_date:
                start_date = datetime.today()

            if not main_file:
                if debug_level == 2:
                    main_file = '1xbet_main.html'
                else:
                    main_file = self.main_file % start_date.strftime('%Y-%m-%d')

            main_url = 'https://1xstavka.ru/line/Football/'
            html = self.get_html(main_file, main_url, get_from_file, is_debug_path)
            self.context = html

            soup = BeautifulSoup(html, 'lxml')

            self.start_detail("Football") 
            football_tag  = soup.find('li', class_='sportMenuActive')
            for league_a in football_tag.select('ul.liga_menu > li > a'):
                league_name = league_a.get_text("\n", strip=True).splitlines()[0]

                if debug_level == 2 and league_name != "England. Premier League":
                    continue

                league_href = league_a['href']
                if not league_href.startswith('http'): league_href = urljoin(self.base_url, league_href)
                if not (league_name.lower().startswith('enhanced') or 
                        league_name.lower().find('statistic') >= 0 or
                        league_name.lower().find('special bets') >= 0
                        ) :
                    if self.start_or_skip_league(league_name):
                        self.process_league(league_href, debug_level, get_from_file, is_debug_path, start_date)
                        if debug_level: break
                        # break #!!!
            
            self.finish_detail() 
        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()
        return source_session


    def process_league(self, league_url, debug_level, get_from_file, is_debug_path, start_date):
        date_pattern = re.compile(r"\d+\.\d+")   #09.04 22:00
        handicap_pattern = re.compile(r"([+-]*)([0-9.,]+)([+-]*)")   #+3.5-
        match_pattern  = re.compile(r'/([0-9]+)[^/]*/$')  #https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/43658291-Liverpool-Porto/
        league_pattern = re.compile(r'Football/([0-9]+)') #https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/43658291-Liverpool-Porto/

        file_name = '1xbet_league.html'
        if debug_level != 2:
            file_name = self.league_file % (start_date.strftime('%Y-%m-%d'), self.league_name.replace(" ", "_"))

        html = self.get_html(file_name, league_url, get_from_file, is_debug_path)
        self.context = html

        soup = BeautifulSoup(html, 'lxml')

        # get subGamesId for all actibe games
        # <a href="line/Football/88637-England-Premier-League/43836787--Bernli/" class="link  ">
        #   <span class="gname">Bournemouth-Burnley</span>
        #   <span class="star" data-type="1" data-fav="187831707"></span>
        # </a>
        sub_game_ids = {}
        li_active = soup.select_one('li.sportMenuActive')
        if not li_active:
            # print('!!! Skip league ' + self.league_name.encode())
            return

        for active_game in li_active.select('a > span.gname'):
            a_parent  = active_game.parent
            mid       = match_pattern.search(a_parent['href'])[1]
            span_star = a_parent.select_one('span.star')
            if span_star:
                data_fav = span_star.get('data-fav',None)
                if data_fav:
                    sub_game_ids[mid] = data_fav

        max_match_date = date.today() + timedelta(3)

        for league_tag in soup.select('div.SSR'):

            league_name_tag = league_tag.select_one('div.c-events__name')
            if not league_name_tag or league_name_tag.get_text().strip().lower() != self.league_name.lower():
                # print('!!! Skip league %s - %s (not equel names)' % (self.league_name.encode(), league_name_tag.get_text().strip().encode()) )
                continue

            header = league_tag.select_one('div.c-bets')
            bet_header = [h.get_text().strip() for h in header.select('div.c-bets__bet')]

            #process matches
            for match_div in league_tag.select('div.c-events__item.c-events__item_game'):
                event_tag  = match_div.select_one('div.c-events__subitem') 
                bet_tag    = match_div.select_one('div.c-bets')
                #get match_date
                match_time = event_tag.select_one('div.c-events__time-info').get_text().strip()
                match_date = date_pattern.search(match_time)[0]
                match_date = self.clear_match_date(match_date, debug_level)

                if match_date > max_match_date:
                    # print(match_date, max_match_date)
                    continue

                #get teams
                teams_tag  = event_tag.select_one('a.c-events__name')
                lines      = teams_tag.get_text("\n", strip=True).splitlines()
                if len(lines) < 2:
                    continue
                name_h     = lines[0]
                name_a     = lines[1]
                if name_h.lower().find('home')>=0 and name_a.lower().find('away')>=0:
                    continue
                if not self.start_or_skip_match(name_h, name_a, match_status=Match.SCHEDULED, match_date=match_date):
                    continue
                # print('%s %s-%s' % (match_date, name_h.encode(), name_a.encode()))
                ##############################################################
                #process main odds
                ##############################################################
                bets = bet_tag.select('a.c-bets__bet')
                for idx, bet in enumerate(bets):
                    odd_value = bet.get_text().strip()
                    if odd_value == '-': odd_value = ''
                    if odd_value:
                        odd_type = bet_header[idx]
                        if odd_type in['O','U']:
                            param_idx = idx+1 if odd_type=='O' else idx-1
                            param     = bets[param_idx].get_text().strip()
                            odd_name  = bet_header[param_idx]
                            if param == '-': param = ''
                            if param:
                                param    = self.clear_total_param(param)
                                odd_name = odd_name + '_' + odd_type
                            else:
                                odd_name = None
                        elif odd_type in['1','2']:
                            param_idx = idx+1 if odd_type=='1' else idx-1
                            odd_name = bet_header[param_idx]
                            if odd_name == 'X':
                                odd_name = odd_type
                                param = None
                            else:
                                #Handicap +3.5-
                                param      = bets[param_idx].get_text().strip()
                                search_obj = handicap_pattern.search(param)
                                odd_name   = odd_name + '_' + odd_type
                                if search_obj[2] == '0':
                                    param = '0'
                                elif odd_type == '1':
                                    param = search_obj[1] + search_obj[2]
                                else: 
                                    param = search_obj[3] + search_obj[2]
                                param = self.clear_handicap_param(param)
                        elif odd_type in['X','1X','2X','12']:
                            odd_name = odd_type
                            param    = None
                        else:
                            odd_name = None
                            param    = None
                        if odd_name:
                            self.add_odd(odd_name, odd_value, param=param)
                ##############################################################
                #process additional odds
                ##############################################################
                #find fatch id
                #https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/43658291-Liverpool-Porto/
                match_id  = match_pattern.search(teams_tag['href'])[1]
                league_id = league_pattern.search(teams_tag['href'])[1]
                event_cnt = event_tag.select_one('a.c-events__more.c-events__more_bets.js-showMoreBets').get_text().strip()
                if event_cnt: event_cnt = int(event_cnt)
                else: event_cnt = 0
                if event_cnt <= 250: event_cnt = 250
                elif event_cnt <= 500: event_cnt = 500
                elif event_cnt <= 750: event_cnt = 750
                elif event_cnt <= 1000: event_cnt = 1000
                elif event_cnt <= 1250: event_cnt = 1250
                else: event_cnt = 1500
                additional_url = ('https://1xstavka.ru/LineFeed/GetGameZip?id=%s&lng=en&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=%s'
                                  % (match_id, event_cnt))
                self.process_add_odds(additional_url, debug_level, get_from_file, is_debug_path)
                ##############################################################
                #process additional statistics
                ##############################################################
                sub_game_id = sub_game_ids[match_id]
                additional_stat_url = ('https://1xstavka.ru/LineFeed/Get1x2_VZip?sports=1&champs=%s&count=50&lng=en&tf=2200000&tz=3&mode=4&subGames=%s&country=1&getEmpty=true'
                                  % (league_id, sub_game_id))
                self.process_add_stats(additional_stat_url, debug_level, get_from_file, is_debug_path)

                self.finish_match()
                if debug_level: break
                # break #!!!

#allSport > ul > li.sportMenuActive > ul > li.active.open > ul > li:nth-child(1) > a


    def process_add_odds(self, add_url, debug_level, get_from_file, is_debug_path, file_suffix='', global_params={}):

        file_name = "1xbet_add"
        if debug_level != 2:
            file_name = self.add_file % (self.name_h.replace(" ", "_")[:20], self.name_a.replace(" ", "_")[:20])
        if file_suffix: file_name += ('_' + file_suffix.replace(' ', '_'))
        file_name += '.json'
        row_data = self.get_html(file_name, add_url, get_from_file, is_debug_path)
        self.context = row_data

        json_data = json.loads(row_data)
        if json_data['Success']:
            groups = json_data['Value']['GE']
            # if type(groups) == type([]): groups = groups[0]
            # groups  = groups['GE']
            for group in groups:
                row_handler = None
                group_num = group['G']
                odd_name  = 'G='+str(group_num)
                # group_handler = ODDS.get('G='+str(group_num), None)
                group_handler = self.get_config('G='+str(group_num))
                if group_handler: 
                    row_handler = group_handler.bookie_handler
                    if row_handler:
                        for row in group['E']:
                            for row_inner in row:
                                method = getattr(self, row_handler)
                                method(odd_name, row_inner, global_params)
                                # globals()[row_handler](self, odd_name, row_inner, global_params)




    def process_add_stats(self, url, debug_level, get_from_file, is_debug_path):

        file_name = "1xbet_add_stats.json"
        if debug_level != 2:
            file_name = self.add_stats_file % (self.name_h.replace(" ", "_")[:20], self.name_a.replace(" ", "_")[:20])
        row_data = self.get_html(file_name, url, get_from_file, is_debug_path)
        self.context = row_data

        json_data = json.loads(row_data)
        groups  = json_data['Value'][0]
        groups  = groups.get('SG',None)
        if not groups:
            return
        for group in groups:
            period_name = group.get('PN', '').strip()
            group_name  = group.get('TG', '').strip()
            cnt         = group['EC']
            group_id    = group['CI']
            if not period_name: full_name = group_name
            elif not group_name: full_name = period_name
            else: full_name = group_name + ' ' + period_name
            if (    not group_name or
                    group_name == 'Corners' and not period_name or
                    group_name == 'Yellow Cards' or
                    group_name == 'Ball Possession' and not period_name or
                    group_name == 'Shots On Target' and not period_name or
                    group_name == 'Offsides' and not period_name or
                    group_name == 'Fouls' and not period_name or
                    group_name == 'Cards. Stats'
                    ):
                #event_cnt
                if cnt: event_cnt = int(cnt)
                else: event_cnt = 0
                if event_cnt <= 250: event_cnt = 250
                elif event_cnt <= 500: event_cnt = 500
                elif event_cnt <= 750: event_cnt = 750
                elif event_cnt <= 1000: event_cnt = 1000
                elif event_cnt <= 1250: event_cnt = 1250
                else: event_cnt = 1500
                #global_params
                global_params = {}
                if group_name == 'Corners': global_params['value_type'] = 'corn'
                elif group_name in ['Yellow Cards','Cards. Stats',]: global_params['value_type'] = 'y_card'
                elif group_name == 'Shots On Target': global_params['value_type'] = 'shots_on_goal'
                elif group_name == 'Offsides': global_params['value_type'] = 'offsides'
                elif group_name == 'Fouls': global_params['value_type'] = 'fouls'
                elif group_name == 'Ball Possession': global_params['value_type'] = 'ball_poss'
                if period_name and period_name.find('1') >= 0: global_params['period'] = 1
                if period_name and period_name.find('2') >= 0: global_params['period'] = 2
                add_url = ('https://1xstavka.ru/LineFeed/GetGameZip?id=%s&lng=en&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=%s'
                           % (group_id,event_cnt)
                           )
                # print('!!!', full_name, add_url)
                self.process_add_odds(add_url, debug_level, get_from_file, is_debug_path, file_suffix=full_name, global_params=global_params)



###########################################################################################
    def add_both_team_to_score(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        G      = odd_data.get('G',None)
        P      = str(odd_data.get('P',0))
        if not G:
            if T in [180,11273]:     # Both Teams To Score
                param  = '0.5'
                bet_type = BetType.ITOTAL_BOTH_OVER
                yes_no   = 1
            elif T in [181,11274]:   # Both Teams To Score
                param  = '0.5'
                bet_type = BetType.ITOTAL_BOTH_OVER
                yes_no   = 0
            elif T in [3523,    # Both Teams To Score - Over & Yes
                       2837,    # Both Teams To Score Yes/No + Total - Both Teams To Score - Yes + Total Over 2.5
                       ]:   
                param    = P
                bet_type = BetType.BOTH_TO_SCORE_AND_TOTAL_OVER
                yes_no   = 1
            elif T == 3524:   # Both Teams To Score - Over & No
                param = P
                bet_type = BetType.BOTH_TO_SCORE_AND_TOTAL_OVER
                yes_no   = 0
            elif T in [3525,    # Both Teams To Score - Under & Yes
                       2839,    # Both Teams To Score Yes/No + Total - Both Teams To Score - Yes + Total Under 2.5
                      ]:   
                param    = P
                bet_type = BetType.BOTH_TO_SCORE_AND_TOTAL_UNDER
                yes_no   = 1
            elif T == 3526:   # Both Teams To Score - Under & No
                param    = P
                bet_type = BetType.BOTH_TO_SCORE_AND_TOTAL_UNDER
                yes_no   = 0
            elif T == 2838:   # Both Teams To Score Yes/No + Total
                param    = P
                bet_type = BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_OVER
                yes_no   = 1
            elif T == 2840:   # Both Teams To Score Yes/No + Total
                param    = P
                bet_type = BetType.NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER
                yes_no   = 1
            else:
                bet_type = None
            if bet_type:
                self.add_odd(odd_name, C, param=self.clear_total_param(param), bet_type=bet_type, yes=yes_no, global_params=global_params)
###########################################################################################
    def add_total(self, odd_name, odd_data, global_params={}):
        C          = odd_data['C']
        T          = odd_data['T']
        P          = odd_data.get('P',None)
        param      = None if not P else self.clear_total_param(str(P))
        yes        = 1
        team       = None
        value_type = None
        if T in [9,11,13,
                 3827,       # Asian Total
                 518,        # Fouls.Penalty Awarded
                 ]:
            bet_type = BetType.TOTAL_OVER
        elif T in [10,12,14,
                   3828,       # Asian Total
                   519,        # Fouls.Penalty Awarded
                   ]:
            bet_type = BetType.TOTAL_UNDER
        elif T == 1082: # Fouls.Penalty Awarded. TEAM SOUTHAMPTON PLAYER TO GET RED CARD - YES
            bet_type   = BetType.TOTAL_OVER
            team       = 'h'
            value_type = 'r_card'
            param    = '0.5'
        elif T == 1084: # Fouls.Penalty Awarded. TEAM SOUTHAMPTON PLAYER TO GET RED CARD - YES
            bet_type   = BetType.TOTAL_OVER
            team       = 'h'
            value_type = 'r_card'
            param    = '0.5'
        elif T == 2772: # Fouls.Penalty Awarded. Red Card - Yes
            bet_type   = BetType.TOTAL_OVER
            value_type = 'r_card'
            param      = '0.5'
        elif T == 2773: # Fouls.Penalty Awarded. Red Card - No
            bet_type   = BetType.TOTAL_UNDER
            value_type = 'r_card'
            param      = '0.5'
        elif T == 1143: # Total Each Team Will Score Under/Over
            bet_type = BetType.ITOTAL_BOTH_UNDER
        elif T == 1145: # Total Each Team Will Score Under/Over
            bet_type = BetType.ITOTAL_BOTH_OVER
        elif T == 1144: # Total Each Team Will Score Under/Over
            bet_type = BetType.ITOTAL_BOTH_UNDER
            yes      = 0
        elif T == 1146: # Total Each Team Will Score Under/Over
            bet_type = BetType.ITOTAL_BOTH_OVER
            yes      = 0
        elif T == 486: # Team Goal In Both Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_OVER
            team     = 'h'
            param    = '0.5'
        elif T == 487: # Team Goal In Both Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_OVER
            team     = 'h'
            yes      = 0
            param    = '0.5'
        elif T == 488: # Team Goal In Both Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_OVER
            team     = 'a'
            param    = '0.5'
        elif T == 489: # Team Goal In Both Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_OVER
            team     = 'a'
            yes      = 0
            param    = '0.5'
        elif T == 8788: # At Least One Team Will Score
            bet_type = BetType.ITOTAL_AT_LEAST_OVER
        elif T == 8789: # At Least One Team Will Score
            bet_type = BetType.ITOTAL_AT_LEAST_OVER
            yes      = 0
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name,C,param=self.clear_total_param(param),bet_type=bet_type,team=team,yes=yes,
                    value_type=value_type,global_params=global_params)
###########################################################################################
    def add_handicap(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        period = None
        if T in (7,
                 3829,     # Asian Handicap
                 ):
            param    = self.clear_handicap_param(str(P))
            bet_type = BetType.HANDICAP
            team     = 'h'
        elif T in(8,
                  3830,    # Asian Handicap
                  ):
            param    = self.clear_handicap_param(str(P))
            bet_type = BetType.HANDICAP
            team = 'a'
        elif T == 1195:   # Handicap In Minute
            bet_type         = BetType.HANDICAP_MINUTES
            h_goals, a_goals = self.decompose_score(P)
            param            = self.clear_handicap_param(str(h_goals/100))
            period           = abs(a_goals)
            team             = 'h'
        elif T == 1196:   # Handicap In Minute
            bet_type         = BetType.HANDICAP_MINUTES
            h_goals, a_goals = self.decompose_score(P)
            param            = self.clear_handicap_param(str(h_goals/100))
            period           = abs(a_goals)
            team             = 'a'
        else:
            team = None
        if team:
            self.add_odd(odd_name, C, param=param, bet_type=bet_type, team=team, period=period, global_params=global_params)
###########################################################################################
    def add_correct_score(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        h_goals, a_goals = self.decompose_score(P)
        param = '%s:%s' %(h_goals,a_goals)
        if T == 731:
            bet_type = BetType.CORRECT_SCORE
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, param=param, bet_type=bet_type, global_params=global_params)
###########################################################################################
    def add_HT_FT(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        p = {15:'1/1',16:'1/X',17:'1/2',18:'X/1',19:'X/X',20:'X/2',21:'2/1',22:'2/X',23:'2/2',
             667:'1/2',668:'1/X',669:'1/1',665:'X/X',666:'X/1',673:'X/2',670:'2/2',671:'2/1',672:'2/X', # Half/Half
             }
        param = p.get(T,None)
        if param:
            self.add_odd(odd_name, C, param=param, global_params=global_params)
###########################################################################################
    def add_goal_interval(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        start_minute, end_minute = self.decompose_score(P)
        if end_minute not in[15,30,45,60,75,90,] or start_minute not in[1,16,31,46,61,76,]: 
            end_minute = None
        bet_type = None
        if T in (2951,   # Goal Interval - Yes
                 2953,   # Goal Interval - No
                 ):
            team     = 'h'
            param    = "0.5"
        elif T in (2952,  # Goal Interval - Yes
                   2954,  # Goal Interval - No
                  ):
            team     = 'a'
            param    = "0.5"
        elif T in [2949,   # Goal In Time Interval - Yes/No
                   2774,   # Any Player To Get Booked During The Match. Cards. Stats
                   2776,   # Team 1 Total In Interval. Cards. Stats
                   2778,   # Team 2 Total In Interval. Cards. Stats
                  ]:   
            if T == 2776: team='h'
            elif T == 2778: team='a'
            else: team     = None
            param    = "0.5"
            bet_type = BetType.TOTAL_OVER_MINUTES
        elif T in [2950,   # Goal In Time Interval - Yes/No
                   2775,   # Any Player To Get Booked During The Match. Cards. Stats
                   2777,   # Team 1 Total In Interval. Cards. Stats
                   2779,   # Team 1 Total In Interval. Cards. Stats
                   ]:   
            if T == 2777: team='h'
            elif T == 2779: team='a'
            else: team     = None
            param    = "0.5"
            bet_type = BetType.TOTAL_UNDER_MINUTES
        else:
            team     = None
            param    = None
            end_minute = None
        if end_minute:
            self.add_odd(odd_name, C, bet_type=bet_type, param=param, team=team, period=end_minute, global_params=global_params)
###########################################################################################
    def add_highest_half(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        bet_type = BetType.HIGHEST_VALUE_HALF
        p = {188:'1',189:'X',190:'2',
             2808:'1',2809:'X',2810:'2',  # Team 1 Scores In Halves
             2811:'1',2812:'X',2813:'2',  # Team 2 Scores In Halves
            }
        param = p.get(T,None)
        if param:
            self.add_odd(odd_name, C, param=param, bet_type=bet_type, global_params=global_params)
###########################################################################################
    def add_both_halves_over(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        param  = str(P)
        bet_type = BetType.TOTAL_BOTH_HALVES_OVER
        if T == 478:
            yes   = 1
            param = '0.50'
        elif T == 479:
            yes   = 0
            param = '0.5'
        elif T == 512: # Total Goals By Halves
            yes   = 1
        elif T == 513: # Total Goals By Halves
            yes   = 0
        elif T == 514: # Total Goals By Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_UNDER
            yes      = 1
        elif T == 515: # Total Goals By Halves
            bet_type = BetType.TOTAL_BOTH_HALVES_UNDER
            yes   = 0
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, param=self.clear_total_param(param), yes=yes, global_params=global_params)
###########################################################################################
    def add_half_to_score_first_goal(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        bet_type = BetType.HALF_TO_SCORE_FIRST_GOAL
        p = {651:'1',652:'2',}
        param = p.get(T,None)
        if param:
            self.add_odd(odd_name, C, bet_type=bet_type, param=param, global_params=global_params)
###########################################################################################
    def add_result_and_total(self, odd_name, odd_data, global_params={}):
        C        = odd_data['C']
        T        = odd_data['T']
        P        = odd_data['P']
        yes      = 1
        bet_type = None
        team     = None
        if T in[196,191,] :      # Team , Result + Total
            bet_type = BetType.W_AND_TOTAL_UNDER
            param    = self.clear_total_param(str(P))
        elif T in[197,192,] :      # Team , Result + Total
            bet_type = BetType.W_AND_TOTAL_OVER
            param    = self.clear_total_param(str(P))
        elif T in[198,193,] :      # Team , Result + Total
            bet_type = BetType.WD_AND_TOTAL_UNDER
            param    = self.clear_total_param(str(P))
        elif T in[199,194,] :      # Team , Result + Total
            bet_type = BetType.WD_AND_TOTAL_OVER
            param    = self.clear_total_param(str(P))
        elif T in[206,211,] :      # Team , Result + Total
            bet_type = BetType.W_AND_TOTAL_UNDER
            yes      = 0
            param    = self.clear_total_param(str(P))
        elif T in[207,212,] :      # Team , Result + Total
            bet_type = BetType.W_AND_TOTAL_OVER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T in[208,213,] :      # Team , Result + Total
            bet_type = BetType.WD_AND_TOTAL_UNDER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T in[209,214,] :      # Team , Result + Total
            bet_type = BetType.WD_AND_TOTAL_OVER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T in [3973,3975,] :      # W1 + Total 1 or W2 + Total 2
            bet_type = BetType.W_AND_ITOTAL_OVER
            param    = self.clear_total_param(str(P))
            yes      = 1
        elif T in [3974,3976,] :      # W1 + Total 1 or W2 + Total 2
            bet_type = BetType.W_AND_ITOTAL_OVER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T in [10334,10336,] :      # W1 + Total 1 or W2 + Total 2
            bet_type = BetType.W_AND_ITOTAL_UNDER
            param    = self.clear_total_param(str(P))
            yes      = 1
        elif T in [10335,10337,] :      # W1 + Total 1 or W2 + Total 2
            bet_type = BetType.W_AND_ITOTAL_UNDER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T == 3984 :      # Outcome + Number Of Goals
            bet_type = BetType.W_AND_TOTAL
            team     = 'h'
            yes      = 1
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T == 3985 :      # Outcome + Number Of Goals
            bet_type = BetType.W_AND_TOTAL
            team     = 'h'
            yes      = 0
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T == 3988 :      # Outcome + Number Of Goals
            bet_type = BetType.W_AND_TOTAL
            team     = 'a'
            yes      = 1
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T == 3989 :      # Outcome + Number Of Goals
            bet_type = BetType.W_AND_TOTAL
            team     = 'a'
            yes      = 0
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T in [10338,10342,] :      # Double Chance + Team 1 Total or Double Chance + Team 2 Total
            bet_type = BetType.WD_AND_ITOTAL_OVER
            param    = self.clear_total_param(str(P))
        elif T in [10339,10343,] :      # Double Chance + Team 1 Total or Double Chance + Team 2 Total
            bet_type = BetType.WD_AND_ITOTAL_OVER
            param    = self.clear_total_param(str(P))
            yes      = 0
        elif T in [10340,10344,] :      # Double Chance + Team 1 Total or Double Chance + Team 2 Total
            bet_type = BetType.WD_AND_ITOTAL_UNDER
            param    = self.clear_total_param(str(P))
        elif T in [10341,10345,] :      # Double Chance + Team 1 Total or Double Chance + Team 2 Total
            bet_type = BetType.WD_AND_ITOTAL_UNDER
            param    = self.clear_total_param(str(P))
            yes      = 0

        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, team=team, param=param, yes=yes, global_params=global_params)
###########################################################################################
    def add_even_odd(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        if T in(182,
                755,   # Individual Total 1 Even/Odd
                766,   # Individual Total 2 Even/Odd
                ):
            param = 'even'
        elif T in(183,
                  757,  # Individual Total 1 Even/Odd
                  767,  # Individual Total 2 Even/Odd
                  ):
            param = 'odd'
        else:
            param = None
        if param:
            self.add_odd(odd_name, C, param=param, global_params=global_params)
###########################################################################################
    def add_race_to_goals(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data['P']
        param = str(P)
        if T in(578,
                ):
            team     = 'h'
            bet_type = BetType.RACE_TO_GOALS
        elif T in(579,
                  ):
            team     = 'a'
            bet_type = BetType.RACE_TO_GOALS
        elif T in(580,
                  ):
            # Neither Team
            team     = None
            bet_type = BetType.ITOTAL_BOTH_UNDER
            param = self.clear_total_param(str(P-0.5))
        else:
            param = None
        if param:
            self.add_odd(odd_name, C, bet_type=bet_type, team=team, param=param, global_params=global_params)
###########################################################################################
    def add_margin(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        team   = None
        param = str(P)
        if T in(4850,
                ):
            yes = 1
        elif T in(4851,
                  ):
            yes = 0
        elif T == 1828:   # Win By
            team = 'h'
            yes  = 1
        elif T == 1829:   # Win By
            team = 'h'
            yes  = 0
        elif T == 1834:   # Win By
            team = 'a'
            yes  = 1
        elif T == 1835:   # Win By
            team = 'a'
            yes  = 0
        elif T == 500:   # To Win By Exactly One Goal Or To Draw
            team  = 'h'
            param = '0,1'
            yes   = 1
        elif T == 501:   # To Win By Exactly One Goal Or To Draw
            team  = 'h'
            param = '0,1'
            yes   = 0
        elif T == 502:   # To Win By Exactly One Goal Or To Draw
            team  = 'a'
            param = '0,1'
            yes   = 1
        elif T == 503:   # To Win By Exactly One Goal Or To Draw
            team  = 'a'
            param = '0,1'
            yes   = 0
        elif T == 2276:   # Total Goals In Interval
            yes   = 1
        elif T == 2277:   # Total Goals In Interval
            yes   = 1
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        else:
            param = None
        if param:
            self.add_odd(odd_name, C, param=param, team=team, yes=yes, global_params=global_params)
###########################################################################################
    def add_wdl(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',None)
        period = P
        yes    = 1
        if T == 1:     # 1x2
            bet_type = BetType.WDL
            param    = 'w'
        elif T == 2:     # 1x2
            bet_type = BetType.WDL
            param    = 'd'
        elif T == 3:     # 1x2
            bet_type = BetType.WDL
            param    = 'l'
        elif T == 4:     # Double Chance
            bet_type = BetType.WDL
            param    = 'wd'
        elif T == 5:     # Double Chance
            bet_type = BetType.WDL
            param    = 'wl'
        elif T == 6:     # Double Chance
            bet_type = BetType.WDL
            param    = 'dl'
        elif T == 1189:     # Result In Minute
            bet_type = BetType.WDL_MINUTE
            param    = 'w'
        elif T == 1190:   # Result In Minute
            bet_type = BetType.WDL_MINUTE
            param    = 'd'
        elif T == 1191:   # Result In Minute
            bet_type = BetType.WDL_MINUTE
            param    = 'l'
        elif T == 179:   # Draw.Score Draw - Yes
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'd'
        elif T == 216:   # Draw.Score Draw - No
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'd'
            yes      = 0
        elif T == 2341:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'w'
        elif T == 2342:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'w'
            yes      = 0
        elif T == 2343:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'l'
        elif T == 2344:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'l'
            yes      = 0
        elif T == 2345:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'd'
        elif T == 2346:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'd'
            yes      = 0
        elif T == 2347:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'wd'
        elif T == 2348:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'wd'
            yes      = 0
        elif T == 2349:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'dl'
        elif T == 2350:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'dl'
            yes      = 0
        elif T == 2351:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'wl'
        elif T == 2352:   # Result And Both Teams To Score
            bet_type = BetType.WDL_AND_BOTH_TEAMS_SCORE
            param    = 'wl'
            yes      = 0
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, param=param, period=period, yes=yes, global_params=global_params)
###########################################################################################
    def add_exact_total(self, odd_name, odd_data, global_params={}):
        C        = odd_data['C']
        T        = odd_data['T']
        P        = odd_data.get('P',0)
        team     = None
        param    = str(P)
        yes      = 1
        bet_type = None
        if T in [2276,    # Total Goals In Interval
                 4555,    # Individual Total 1 Exact Number Of Goals
                 4563,    # Individual Total 2 Exact Number Of Goals
                 ]:   
            if P == 0:
                bet_type = BetType.TOTAL_UNDER
                param    = self.clear_total_param('0.5')
        elif T in [2277, # Total Goals In Interval
                   1747, # Team 1 To Score N Goals
                   1749, # Team 2 To Score N Goals
                   1739, # Individual Total Interval - 1. Cards. Stats
                   1740, # Individual Total Interval - 2. Cards. Stats
                   2309, # Total Interval.. Cards. Stats
                   ]:   
            yes   = 1
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T in [1748, # Team 1 To Score N Goals
                   1750, # Team 2 To Score N Goals
                   ]:   
            yes   = 0
            p_start, p_end = self.decompose_score(P)
            param = ','.join(map(str,range(p_start,p_end+1)))
        elif T == 4548:     # Exact Number Of Goals
            if P == 0:
                bet_type = BetType.TOTAL_UNDER
                param    = self.clear_total_param('0.5')
        elif T == 4549:     # Exact Number Of Goals
            if P == 0:
                bet_type = BetType.TOTAL_OVER
                param    = self.clear_total_param('0.5')
            else:
                yes = 0
        elif T in [4550,4551,]:     # Exact Number Of Goals
            if T == 4551: yes = 0
            p_start, p_end = self.decompose_score(P)
            param          = ','.join(map(str,range(p_start,p_end+1)))
        elif T in [4552,   # Exact Number Of Goals
                   4556,   # Individual Total 1 Exact Number Of Goals
                   4564,   # Individual Total 2 Exact Number Of Goals
                   1711,   # Individual Total Interval - 1. Cards. Stats
                   1712,   # Individual Total Interval - 2. Cards. Stats
                   2310,   # Total Interval.. Cards. Stats
                   ]:     
            bet_type = BetType.TOTAL_OVER
            param          = self.clear_total_param(str(P-0.5))
        else:
            param = None
        if param:
            self.add_odd(odd_name, C, bet_type=bet_type, param=param, team=team, yes=yes, global_params=global_params)
###########################################################################################
    def add_result_halves(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        yes    = 1
        team   = None
        if T == 504:   # Results. Halves
            team     = 'h'
            bet_type = BetType.WIN_LEAST_ONE_HALF
        elif T == 505:   # Results. Halves
            team     = 'h'
            bet_type = BetType.WIN_LEAST_ONE_HALF
            yes      = 0
        elif T == 506:   # Results. Halves
            team     = 'a'
            bet_type = BetType.WIN_LEAST_ONE_HALF
        elif T == 507:   # Results. Halves
            team     = 'a'
            bet_type = BetType.WIN_LEAST_ONE_HALF
            yes      = 0
        elif T == 508:   # Results. Halves
            team     = 'h'
            bet_type = BetType.WIN_BOTH
        elif T == 509:   # Results. Halves
            team     = 'h'
            bet_type = BetType.WIN_BOTH
            yes      = 0
        elif T == 510:   # Results. Halves
            team     = 'a'
            bet_type = BetType.WIN_BOTH
        elif T == 511:   # Results. Halves
            team     = 'a'
            bet_type = BetType.WIN_BOTH
            yes      = 0
        elif T == 516:   # Results. Halves
            bet_type = BetType.DRAW_IN_EITHER_HALF
        elif T == 517:   # Results. Halves
            bet_type = BetType.DRAW_IN_EITHER_HALF
            yes      = 0
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, team=team, yes=yes, global_params=global_params)
###########################################################################################
    def add_result_teams_to_score(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        team   = None
        yes    = 1
        if T in [2537,    # Result / Teams To Score
                 200,     # Team 1 Win To Nil
                 ]:   
            team     = 'h'
            bet_type = BetType.WIN_TO_NIL
        elif T in [2539,  # Result / Teams To Score
                   195,   # Team 2 Win To Nil
                   ]:   
            team     = 'a'
            bet_type = BetType.WIN_TO_NIL
        elif T == 205:    # Team 1 Win To Nil - No
            team     = 'h'
            bet_type = BetType.WIN_TO_NIL
            yes      = 0
        elif T == 210:    # Team 2 Win To Nil - No
            team     = 'a'
            bet_type = BetType.WIN_TO_NIL
            yes      = 0
        elif T == 1808:    #Win To Nil - Yes
            bet_type = BetType.WIN_TO_NIL
        elif T == 1809:    #Win To Nil - No
            bet_type = BetType.WIN_TO_NIL
            yes      = 0
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, team=team, yes=yes, global_params=global_params)
###########################################################################################
    def add_both_team_to_score_in_halves(self, odd_name, odd_data, global_params={}):
        C        = odd_data['C']
        T        = odd_data['T']
        bet_type = BetType.BOTH_TO_SCORE_AT_1_2
        if T == 2841:   # Both Teams To Score In Halves
            param = '1\\1'
        elif T == 2842:   # Both Teams To Score In Halves
            param = '0\\1'
        elif T == 2843:   # Both Teams To Score In Halves
            param = '1\\0'
        elif T == 2844:   # Both Teams To Score In Halves
            param = '0\\0'
        else:
            bet_type = None
        if bet_type:
            self.add_odd(odd_name, C, bet_type=bet_type, param=param, global_params=global_params)
###########################################################################################
    def add_first_goal_interval(self, odd_name, odd_data, global_params={}):
        C      = odd_data['C']
        T      = odd_data['T']
        P      = odd_data.get('P',0)
        start_minute, end_minute = self.decompose_score(P)
        if end_minute not in[15,30,45,60,75,90,] or start_minute not in[1,16,31,46,61,76,]: 
            end_minute = None
        if T in [2854,2856,]:
            pass
        else:
            end_minute = None
        if end_minute:
            end_minute = str(end_minute)
        if end_minute:
            self.add_odd(odd_name, C, param=end_minute, global_params=global_params)


    def add_odd(self, odd_name, odd_value, param=None, team=None, value_type=None, 
                bet_type=None, yes=None, period=None,
                global_params={}):
        odd_params = self.get_config(odd_name)
        # odd_params = ODDS.get(odd_name, None)
        if odd_params:
            #value_type
            value_type_real = global_params.get('value_type',None)
            if not value_type_real:
                value_type_real = value_type if value_type else odd_params.value_type
            #period
            period_real = global_params.get('period',None)
            if period_real==None:
                period_real = period
            bet_type = bet_type if bet_type else odd_params.bet_type.slug
            if yes==None:
                yes = odd_params.yes
            else:
                if yes == 1:
                    yes = "yes"
                elif yes == 0:
                    yes = "no"
            odd = {
                      "bet_type":bet_type, 
                      "odd_value":odd_value, 
                      "team":team if team else odd_params.team, 
                      "period":odd_params.period if period_real==None else period_real, 
                      "param":param if param else odd_params.param, 
                      "yes":yes, 
                      "value_type": ValueType.MAIN if not value_type_real else XBET_VALUE_TYPES[value_type_real],
                      "odd_bookie_config":odd_params,
                      }
            self.odds.append(odd)


    def decompose_score(self, param):
        ''' Decompose nuber to score
            Examples:
            1.002  - 1 2
            31.045 - 31 45
        '''
        h = int(param)
        a = round((param - float(h))*1000)
        return h, a



    def clear_match_date(self, match_date, debug_level):
        ''' convert date from dd.mm to date 
            depenfing of current year
        '''
        dm = match_date.split('.')
        d = int(dm[0])
        m = int(dm[1])
        today = datetime.today()
        if debug_level == 2:
            y = 2019
        elif m <= 2 and today.month >= 11:
            y = today.year + 1
        elif m > 11 and today.month <= 2:
            y = today.year - 1
        else:
            y = today.year
        return date(y, m, d)


