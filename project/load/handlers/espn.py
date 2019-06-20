import os
from datetime import datetime, date, timedelta
import logging
import re
import json

from bs4 import BeautifulSoup

from django.utils import timezone

from load.models import CommonHandler
from load.exceptions import TooMamyErrors

logger = logging.getLogger(__name__)


def _get_statistics(data, name_field, param_field, value_field):
    ''' Get value by formula
        [x for x in statistics if x['name']=="totalShots"][0]['displayValue']
    '''
    return [x for x in data if x[name_field]==param_field][0][value_field]


###################################################################
class ESPNHandler(CommonHandler):

    DEBUG_DATE = date(2019, 2, 2)
    matches_file = 'espn_matches.html'

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return ESPNHandler.objects.get(
                        sport = cls.get_sport(), 
                        slug=ESPNHandler.SRC_ESPN)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path('espn') 


    def process(self, is_debug=False, get_from_file=False, is_debug_path=True, start_date=None):
        '''Main method to load site''' 

        try:
            self.start_load('Main handler', is_debug=is_debug)

            if is_debug and not start_date:
                get_from_file = True
            if not get_from_file:
                dat = start_date if start_date else self.DEBUG_DATE
            else:
                dat = self.get_load_date()
            while dat <= timezone.now().date():

                self.set_load_date(load_date=dat, is_set_main=True)
                self.process_date(dat, is_debug, get_from_file, is_debug_path)

                dat += timedelta(days=1)
                if is_debug: break
        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()


    def process_date(self, match_date, is_debug, get_from_file, is_debug_path):
        ''' Process single date
            Site http://www.espn.com

            Arguments:
            match_date  - Date 
            is_debug    - is debugging

        '''

        url = 'http://www.espn.com/soccer/scoreboard/_/league/all/date/' + match_date.strftime('%Y%m%d')
        html = self.get_html(self.matches_file, url, get_from_file, is_debug_path)
        self.context = 'html:\r' + str(html)

        soup = BeautifulSoup(html, 'html.parser')
        script_pattern = re.compile(r"(\{.+?\]\});")   #({...]});
        time_pattern = re.compile(r"^(\d+)")   #65&amp;#39

        #find script with "window.espn.scoreboardData"
        script = str(soup.find('script', string=re.compile("window.espn.scoreboardData")).string)
        self.context = 'script:\r' + script
        matches_json = script_pattern.search(script)[1]
        self.context = 'matches_json:\r' + matches_json
        matches = json.loads(matches_json)
        scores = matches['scores']
        for score in scores:
            self.context = 'score:\r' + str(score)
            league_json = score['leagues'][0]

            try:
                league_name = league_json['name']
                if not self.start_or_skip_league(league_name):
                    #skip league
                    continue
                    
                calendar = league_json['calendar']
                calendar_type = league_json['calendarType']
                start_date = None
                end_date   = None
                if calendar_type == 'day':
                    start_date = min(calendar)
                    end_date   = max(calendar)
                else:
                    calendar_entries = calendar[0]['entries']
                    start_date = min([e['startDate'] for e in calendar_entries])
                    end_date   = max([e['endDate'] for e in calendar_entries])
                start_date=datetime.strptime(start_date[:10], "%Y-%m-%d").date()
                end_date=datetime.strptime(end_date[:10], "%Y-%m-%d").date()
                # season_name = score['season']['year']
                season_name = None
                self.create_league_session(start_date, end_date, self, name=season_name)
                events = score['events']
                for event in events:
                    self.context = 'event:\r' + str(event)
                    # event_date = datetime.strptime(str(event['date'])[:10], '%Y-%m-%d').date()
                    competition = event['competitions'][0]
                    #is match finished
                    status_info   = event['status']
                    is_result     = status_info['type']['completed']
                    status_detail = status_info['type']['detail']
                    if is_result and 'FT' in status_detail:
                        #match finished
                        id_h   = None
                        id_a   = None
                        statistics_h   = None
                        statistics_a   = None
                        #Process home and away team
                        for competitor in competition['competitors']:
                            home_away = competitor['homeAway']
                            if home_away == 'home':
                                id_h         = competitor['id']
                                competitor_h = competitor["team"]
                                statistics_h = competitor.get("statistics", None)
                            elif home_away == 'away':
                                id_a         = competitor['id']
                                competitor_a = competitor["team"]
                                statistics_a = competitor.get("statistics", None)
                            else:
                                continue
                        if not statistics_h or not statistics_a:
                            #Empty match statistics
                            continue

                        try:

                            name_h = competitor_h['name']
                            name_a = competitor_a['name']
                            if not self.start_or_skip_match(name_h, name_a):
                                #skip match (event)
                                continue

                            #save match info
                            # "statistics":[{"displayValue":"0","name":"appearances","abbreviation":"APP"},
                            #               {"displayValue":"6","name":"foulsCommitted","abbreviation":"FC"},
                            #               {"displayValue":"6","name":"wonCorners","abbreviation":"CW"},
                            #               {"displayValue":"1","name":"goalAssists","abbreviation":"A"},
                            #               {"displayValue":"71.6","name":"possessionPct","abbreviation":"PP"},
                            #               {"displayValue":"18","name":"shotAssists","abbreviation":"SHAST"},
                            #               {"displayValue":"4","name":"shotsOnTarget","abbreviation":"ST"},
                            #               {"displayValue":"1","name":"totalGoals","abbreviation":"G"},
                            #               {"displayValue":"21","name":"totalShots","abbreviation":"SH"}
                            #             ]

                            shots_h           = int(_get_statistics(statistics_h, 'name', 'totalShots', 'displayValue'))
                            shots_a           = int(_get_statistics(statistics_a, 'name', 'totalShots', 'displayValue'))
                            shots_on_target_h = int(_get_statistics(statistics_h, 'name', 'shotsOnTarget', 'displayValue'))
                            shots_on_target_a = int(_get_statistics(statistics_a, 'name', 'shotsOnTarget', 'displayValue'))
                            fouls_h           = int(_get_statistics(statistics_h, 'name', 'foulsCommitted', 'displayValue'))
                            fouls_a           = int(_get_statistics(statistics_a, 'name', 'foulsCommitted', 'displayValue'))
                            corners_h         = int(_get_statistics(statistics_h, 'name', 'wonCorners', 'displayValue'))
                            corners_a         = int(_get_statistics(statistics_a, 'name', 'wonCorners', 'displayValue'))
                            possession_h      = _get_statistics(statistics_h, 'name', 'possessionPct', 'displayValue')
                            possession_a      = _get_statistics(statistics_a, 'name', 'possessionPct', 'displayValue')
                            self.h.set_stats(
                                                goals=0, y_cards=0, r_cards=0, penalties=0,
                                                goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0,
                                                goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0,
                                                init_goals_minutes=True, init_y_cards_minutes=True, 
                                                init_r_cards_minutes=True, init_goals_times=True,
                                                shots=shots_h, shots_on_target=shots_on_target_h,
                                                fouls=fouls_h, corners=corners_h,
                                                possession=possession_h)
                            self.a.set_stats(
                                                goals=0, y_cards=0, r_cards=0, penalties=0,
                                                goals_1st=0, y_cards_1st=0, r_cards_1st=0, penalties_1st=0,
                                                goals_2nd=0, y_cards_2nd=0, r_cards_2nd=0, penalties_2nd=0,
                                                init_goals_minutes=True, init_y_cards_minutes=True, 
                                                init_r_cards_minutes=True, init_goals_times=True,
                                                shots=shots_a, shots_on_target=shots_on_target_a,
                                                fouls=fouls_a, corners=corners_a,
                                                possession=possession_a)
                            details = competition['details']
                            for detail in details:
                                self.context = 'detail:\r' + str(detail)
                                #"clock":{"displayValue":"65&amp;#39;","value":3885}
                                time_row = detail['clock']['displayValue']
                                minute = int(time_pattern.search(time_row)[1])
                                team_id = detail['team']['id']
                                if team_id == id_h:
                                    # Home team
                                    t = self.h
                                elif team_id == id_a:
                                    # Away team
                                    t = self.a
                                if detail['redCard']:      t.add_event(minute, r_cards=1)
                                if detail['yellowCard']:   t.add_event(minute, y_cards=1)
                                if detail['scoringPlay']:  t.add_event(minute, goals=1)
                                if detail['penaltyKick']:  t.add_event(minute, penalties=1)

                            self.finish_match()

                        except TooMamyErrors:
                            raise
                        except Exception as e:
                            self.handle_exception(e)
                        finally:
                            self.context = None

                self.finish_league()

            except TooMamyErrors:
                raise
            except Exception as e:
                self.handle_exception(e)
            finally:
                self.context = None

