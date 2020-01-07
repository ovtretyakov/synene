import os
import time
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

import requests
import re

from urllib.request import urljoin
from bs4 import BeautifulSoup, Comment, element

from django.template.defaultfilters import slugify

from project.core.models import Country, Match
from project.betting.models import ValueType, BetType
from ..models import CommonHandler
from ..exceptions import TooMamyErrors

logger = logging.getLogger(__name__)


PARIMATCH_STATS = {
            "match stat":      "match_stat", 
            "corn.":           "corn",
            "y.card":          "y_card",
            "fouls":           "fouls",
            "shots on goal":   "shots_on_goal",
            "shots all":       "shots_all",
            "offsides":        "offsides",
            "ball poss.(%)":   "ball_poss",
            }


PARIMATCH_VALUE_TYPES = {
            "main": ValueType.MAIN,
            "match_stat": ValueType.MAIN,
            "corn": ValueType.CORNER,
            "y_card": ValueType.Y_CARD,
            "r_card": ValueType.R_CARD,
            "fouls": ValueType.FOUL,
            "shots_on_goal": ValueType.SHOT_ON_GOAL,
            "shots_all": ValueType.SHOT,
            "offsides": ValueType.OFFSIDE,
            "ball_poss": ValueType.POSSESSION,
            "penalty": ValueType.PENALTY,
            }


###################################################################
class ParimatchHandler(CommonHandler):

    main_file   = "parimatch_main.html"
    leagues_file0 = "parimatch_leagues.html"
    leagues_file = "parimatch_leagues_%s.html"

    class Meta:
        proxy = True

    @classmethod
    def get(cls):
        return cls.objects.get(
                        sport = cls.get_sport(), 
                        slug=cls.SRC_PARIMATCH)

    @classmethod
    def get_handler_dir(cls):
        hdir = super().get_handler_dir()
        return hdir.path("parimatch") 


    def process(self, debug_level=0, get_from_file=False, is_debug_path=True, start_date=None, main_file=None):
        """ Process site
          Site https://www.parimatch.com/en/
        """
        source_session = None
        try:
            source_session = self.start_load(is_debug=debug_level)

            if not main_file:
                main_file = self.main_file

            main_url = "https://www.parimatch.com/en/"
            html = self.get_html(main_file, main_url, get_from_file, is_debug_path)
            self.context = html

            soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")

            if debug_level >= 2:
                self.start_detail("Football") 
                self.process_all_leagues(None, debug_level, get_from_file, is_debug_path, is_football_stats=False)
            else:
                football_tag  = soup.find("a", href="#Football")
                football_stats_tag  = soup.find("a", href="#Football/Stats")
                leagues = football_tag.next_sibling.find_all("li")
                self.start_detail("Football") 
                for j in [1,2]:  #1 - Football, 2 - Football Stats

                    is_football_stats = (j==2)

                    all_lieague_id = (league.a["hd"] for league in leagues)
                    i = 0
                    all_lieague_id = []
                    for league in leagues:
                        all_lieague_id.append(league.a["hd"])
                        i += 1
                        if i>=10:
                            league_ids = "%2C".join(all_lieague_id)
                            self.process_all_leagues(league_ids, debug_level, get_from_file, is_debug_path, is_football_stats)
                            i = 0
                            all_lieague_id = []

                    if all_lieague_id:
                        league_ids = "%2C".join(all_lieague_id)
                        self.process_all_leagues(league_ids, debug_level, get_from_file, is_debug_path, is_football_stats)
                    
                    #next - process football stats
                    self.finish_detail() 
                    leagues = football_stats_tag.next_sibling.find_all("li")
                    self.start_detail("Stats") 
            
            self.finish_detail() 
        except Exception as e:
            self.handle_exception(e, raise_finish_error=False)
        finally:
            self.finish_load()
        return source_session


    def process_all_leagues(self, league_ids, debug_level, get_from_file, is_debug_path, is_football_stats):
        """ Process all leagues
            Site https://www.parimatch.com/en/

            Arguments:
            league_ids
        """

        if league_ids:
            file_name = self.leagues_file % league_ids
            url = "https://www.parimatch.com/en/bet.html?hd=" + league_ids
        else:
            file_name = self.leagues_file0
            url = "https://www.parimatch.com/en/bet.html?hd="

        html = self.get_html(file_name, url, get_from_file, is_debug_path)
        self.context = html
        soup = BeautifulSoup(html, "lxml", from_encoding="utf-8")

        odd_list = soup.select("div#oddsList")[0]
        leagues  = odd_list.select("div.container")
        for league in leagues:
            self.context = league
            self.process_single_league(league, is_football_stats)



    def process_single_league(self, league_html, is_football_stats):
        """ Process single league
            Site https://www.parimatch.com/en/

            Arguments:
            league_html  - html info of league
        """
        league_name = league_html.h3.get_text().strip()
        if league_name.lower().find("comparison") < 0 and league_name.lower().find("specials") < 0:

            #remove ending Match stats
            #Football. UEFA Champions League. Match stats
            if league_name.upper().endswith("MATCH STATS"):
                league_name = league_name[:-11].strip()
            if league_name.endswith("."):
                league_name = league_name[:-1].strip()

            league_slug = league_name
            if league_slug.upper().startswith("FOOTBALL"):
                league_slug = league_slug[8:].strip()
                if league_slug.startswith("."):
                    league_slug = league_slug[1:].strip()
            league_slug = slugify(league_slug)[:50]
            if not self.start_or_skip_league(league_name, league_slug=league_slug):
                #skip league
                return

            # find odd header
            header_tr = league_html.find("tr")
            header = [h.get_text() for h in header_tr.find_all("th")]

            # process matches
            match_name = None
            old_match_name = None
            for match in league_html.find_all("tbody", class_=["row1","row2"]):
                self.context = match
                if "props" not in(match["class"]):
                    m2 = match.next_sibling
                    if not m2 == None and "props" in(m2["class"]):
                        #Second parts of odds - make list
                        match_odds = [match, m2]
                    else:
                        match_odds = [match]
                        self.context = match_odds
                    match_name = self.process_match(match_odds, header, is_football_stats, old_match_name)
                    if match_name:
                        old_match_name = match_name
            if old_match_name:
                self.finish_match()
            self.finish_league() 


    def process_match(self, match_odds, header, is_football_stats, old_match_name):
        date_pattern = re.compile(r"\d+/\d+/\d+") #evd 17/03/19 18:30 evd
        match_date   = None
        name_h       = None
        name_a       = None
        match_detail = None
        match_stat   = None
        is_main_line = None
        match_name = None
        for match_odd in match_odds:
            self.context = match_odd
            if not name_h:
                is_main_line = True
                #get match_date
                date_tag     = match_odd.select("tr > td")[1]
                date_comment = date_tag.find(text=lambda text:isinstance(text, Comment))
                date_str = date_pattern.search(date_comment)[0]
                match_date = datetime.strptime(date_str, "%d/%m/%y").date()
                #get teams
                teams_tag = match_odd.select_one("tr > td.l")
                name_h, name_a, match_stat = self._get_teams(teams_tag, is_football_stats)
                match_name = name_h + " - " + name_a
                if is_football_stats and not match_stat:
                    #unknown match stat - skip
                    return
                if (name_h.lower().find("home")>=0 and name_a.lower().find("away")>=0 or
                    name_h.lower().find("home")>=0 and name_a.lower().find("guests")>=0
                    ):
                    #skip teams "home" and "away"
                    return
                if old_match_name and match_name != old_match_name:
                    self.finish_match()
                if not old_match_name or match_name != old_match_name:
                    if not self.start_or_skip_match(name_h, name_a, match_status=Match.SCHEDULED, match_date=match_date):
                        return
            else:
                is_main_line = False


            #Process odd lines
            odd_prefix = ""  #contain period name if additional part is processing
            for line in match_odd.select("tbody > tr"):
                try:
                    self.context = line
                    tds = line.select("tr > td")
                    if line.has_attr("class") and line["class"][0] == "bk":
                        #Process main odds
                        if not is_main_line:
                            #get period name 
                            #1-st half_ or 2-nd half_
                            s = tds[1].get_text().strip().replace(":","")
                            if s: odd_prefix = s + "_"
                        self.process_bk(tds, match_detail, header, match_stat, odd_prefix)
                    else:
                        #Process additional odds
                        td2 = tds[1]
                        if not td2.has_attr("class"):
                            tag = td2.select_one("td > table.ps")
                            self.process_ps(tag, match_detail, match_stat)
                        elif td2.get("class")[0] == "p2r":
                            self.process_p2r(td2, match_detail, match_stat)
                        elif td2.get("class")[0] == "dyn":
                            self.process_dyn(td2, match_detail, match_stat)
                except TooMamyErrors:
                    raise
                except Exception as e:
                    print("Exception", str(e))
                    self.handle_exception(e)
        # self.finish_match()
        return match_name


    def process_bk(self, tds, match_detail, header, match_stat, odd_prefix):
        """Process main odds <tr class="bk">"""
        for i in range(3, len(header)):
            if header[i] in("Hand.","Total","1","X","2","1X","12","X2","iTotal"):
                td = self.get_td(tds, i)
                if td and td.get_text().strip():
                    odd_name = odd_prefix + header[i]
                    if header[i] == "Hand.":
                        odd_name = odd_prefix + "Hand"
                        params  = td.get_text("\n", strip=True).splitlines()
                        odds    = td.next_sibling.get_text("\n", strip=True).splitlines()
                        self.add_odd(odd_name, odds[0], param=self.clear_handicap_param(params[0]), team="h", value_type=match_stat)
                        self.add_odd(odd_name, odds[1], param=self.clear_handicap_param(params[1]), team="a", value_type=match_stat)
                    elif header[i] == "Total":
                        odd_name   = odd_prefix + "Total"
                        param      = td.get_text().strip()
                        over_tag   = td.next_sibling
                        under_tag  = over_tag.next_sibling
                        over_name  = odd_name + "_Over"
                        under_name = odd_name + "_Under"
                        self.add_odd(over_name, over_tag.get_text().strip(), param=self.clear_total_param(param), value_type=match_stat)
                        self.add_odd(under_name, under_tag.get_text().strip(), param=self.clear_total_param(param), value_type=match_stat)
                    elif header[i] == "iTotal":
                        odd_name   = odd_prefix + "iTotal"
                        params     = td.get_text("\n", strip=True).splitlines()
                        over_tag   = td.next_sibling
                        under_tag  = over_tag.next_sibling
                        over_odds  = [s.replace("\xa0","").strip() for s in over_tag.strings]
                        under_odds = [s.replace("\xa0","").strip() for s in under_tag.strings]
                        over_name  = odd_name + "_Over"
                        under_name = odd_name + "_Under"
                        if over_odds[0]:
                            self.add_odd(over_name, over_odds[0], param=self.clear_total_param(params[0]), team="h", value_type=match_stat)
                        if under_odds[0]:
                            self.add_odd(under_name, under_odds[0], param=self.clear_total_param(params[0]), team="h", value_type=match_stat)
                        if over_odds[1]:
                            self.add_odd(over_name, over_odds[1], param=self.clear_total_param(params[1]), team="a", value_type=match_stat)
                        if under_odds[1]:
                            self.add_odd(under_name, under_odds[1], param=self.clear_total_param(params[1]), team="a", value_type=match_stat)
                    else:
                        odd_name   = odd_prefix + header[i]
                        odd        = td.get_text().strip()
                        self.add_odd(odd_name, odd, value_type=match_stat)
  

    def process_ps(self, tag, match_detail, match_stat):
        param_pattern = re.compile(r"\(([^)]+)\)\s*([0-9.,]+)") #(+2.0) 2.50
        over_pattern  = re.compile(r"\(([^)]+)\)\s*over\s*([0-9.,]*)") #(1.5) over 14.5
        under_pattern = re.compile(r"under\s*([0-9.,]*)")              #under 1.49
        inner_table = tag.find("table", class_="ps")
        # Add. handicaps:
        # Add. totals:
        # Goals
        # HT/FT
        # Stats: Violations
        table_type = tag.find("th").get_text()
        ###################################################################
        if table_type == "Add. handicaps:":
            trs = inner_table.find_all("tr")
            for i in [1,2]:
                tr = trs[i]
                team_name = tr.find("td").get_text()
                if team_name.find(self.name_h) >= 0: team = "h"
                elif team_name.find(self.name_a) >= 0: team = "a"
                else: team=""
                if team:
                    td = tr.select_one("td:nth-of-type(2)")
                    for line in td.get_text().split(";"):
                        search_obj = param_pattern.search(line)
                        if search_obj:
                            param = search_obj.group(1).replace(",",".").strip()
                            value = search_obj.group(2).replace(",",".").strip()
                            self.add_odd("Hand", value, param=self.clear_handicap_param(param), team=team, value_type=match_stat)
        ###################################################################
        elif table_type == "Add. totals:":
            trs = inner_table.find_all("tr")
            for i in range(1,len(trs)):
                tr = trs[i]
                #first tag "td" contains taem name
                team_name = tr.find("td").get_text().strip()
                if team_name.find(self.name_h) >= 0: 
                    team = "h"
                    td = tr.select_one("td:nth-of-type(2)")
                elif team_name.find(self.name_a) >= 0: 
                    team = "a"
                    td = tr.select_one("td:nth-of-type(2)")
                else: 
                    team = "" #empty team. data contains match totals
                    td = tr.select_one("td:nth-of-type(1)")
                #content td-tag:
                # <td>
                #   (2.0) over 
                #   <u><a>5.50</a></u>
                #   ; under 
                #   <u><a>1.15</a></u>
                #   ; (1.5) over 
                #   <u><a >2.75</a></u>
                #   ; under
                #   <u class=""><a>1.45</a></u>
                #   ;
                # </td>        
                lines = td.get_text().split(";")
                for line in lines:
                    search_obj = over_pattern.search(line)
                    if search_obj:
                        bet_type = "iTotal_Over" if team else "Total_Over"
                        param    = search_obj.group(1).replace(",",".").strip()
                        value    = search_obj.group(2).replace(",",".").strip()
                        if value:
                            self.add_odd(bet_type, value, param=self.clear_total_param(param), team=team, value_type=match_stat)
                    else:
                        search_obj = under_pattern.search(line)
                        if search_obj:
                            bet_type   = "iTotal_Under" if team else "Total_Under"
                            value    = search_obj.group(1).replace(",",".").strip()
                            if value:
                                self.add_odd(bet_type, value, param=self.clear_total_param(param), team=team, value_type=match_stat)
        ###################################################################
        elif table_type in("Goals", "Violations"):
            td = inner_table.find("td", class_="p2r")
            for child in td.children:
                if child.name == "i":
                    odd_value = None
                    suffix    = None
                    odd_name = child.get_text().replace(":","").strip()
                    odd_name, is_found = self.transform_by_team(odd_name, self.name_h)
                    if is_found:
                        team0 = "h"
                    else:
                        odd_name, is_found = self.transform_by_team(odd_name, self.name_a)
                        team0 = "a" if is_found else ""
                elif child.name == "u":
                    value = child.get_text().replace(",",".").strip()
                    if suffix: odd_name_real = odd_name + " " + suffix
                    else: odd_name_real = odd_name
                    self.add_odd(odd_name_real, value, team=team, value_type=match_stat)
                else:
                    child_text = self.get_bs4_str(child).replace(";","").strip()
                    if child_text:
                        suffix = child_text 
                        suffix_h, is_found_h = self.transform_by_team(suffix, self.name_h)
                        suffix_a, is_found_a = self.transform_by_team(suffix, self.name_a)
                        if is_found_h and is_found_a:
                            suffix = "both"
                            team = team0
                        elif is_found_h:
                            team = "h"
                            suffix = suffix_h
                        elif is_found_a:
                            team = "a"
                            suffix = suffix_a
                        else:
                            team = team0
        ###################################################################
        elif table_type == "HT/FT":
            for td in inner_table.select("tr > td"):
                lines = td.get_text("\n", strip=True).splitlines()
                j = 0
                for line in lines:
                    line = line.replace(";","").strip()
                    if line:
                        if j == 0:
                            odd_name = line
                            j += 1
                        else:
                            value = line
                            j     = 0
                            self.add_odd(odd_name, value, value_type=match_stat)


    def process_p2r(self, tag, match_detail, match_stat):
        for tag_i in tag.find_all("i", class_="p2r"):
            odd_name = tag_i.get_text().replace(":","").strip()
            odd_name, is_found = self.transform_by_team(odd_name, self.name_h)
            if is_found:
                team = "h"
            else:
                odd_name, is_found = self.transform_by_team(odd_name, self.name_a)
                team = "a" if is_found else ""

            next_tag = tag_i.next_sibling
            yes_text_str = self.get_bs4_str(next_tag)
            if yes_text_str.find("yes") >= 0: yes_text = "yes"
            elif yes_text_str.find("even") >= 0: yes_text = "even"
            else: yes_text = ""
            no_text  = ""
            if not yes_text or yes_text_str.find("no")>=0 or yes_text_str.find("odd")>=0:
                #somting wrong
                continue
            next_tag = next_tag.next_sibling
            yes_odd  = None
            no_odd   = None
            if next_tag and next_tag.name != "i":
                yes_odd = self.get_bs4_str(next_tag)
                if not (yes_odd.find("no") >= 0 or yes_odd.find("odd") >= 0):
                    next_tag = next_tag.next_sibling
                else:
                    yes_odd = None
                if next_tag and next_tag.name != "i":
                    no_text_str = self.get_bs4_str(next_tag)
                    if no_text_str.find("no") >= 0: no_text = "no"
                    elif no_text_str.find("odd") >= 0: no_text = "odd"
                    else: no_text = ""
                    if no_text:
                        next_tag = next_tag.next_sibling
                        if next_tag and next_tag.name != "i":
                            no_odd = next_tag.get_text().strip()
            if yes_odd:
                self.add_odd(odd_name + " " + yes_text, yes_odd, team=team, value_type=match_stat)
            if no_odd:
                self.add_odd(odd_name + " " + no_text, no_odd, team=team, value_type=match_stat)


    def process_dyn(self, tag, match_detail, match_stat):
        param_pattern = re.compile(r"(.+)/(.+)")   #Liverpool Win / Liverpool Win
        score_pattern = re.compile(r"(\d+):(\d+)") #Liverpool to win 1:0, 2:0 or 2:1
        name_pattern1 = re.compile(r"Total Goals\s*([0-9.,]+)\s*/\s*Both teams to score") #Total Goals 2,5 / Both teams to score
        over_under_pattern = re.compile(r"(over|under)\s*([0-9.,]+)", flags=re.IGNORECASE) #Over 2.5
        tag_i = tag.find("i", class_="p2r")
        odd_name = tag_i.get_text().replace(":","").strip()
        odd_name, is_found = self.transform_by_team(odd_name, self.name_h)
        if is_found:
            team0 = "h"
        else:
            odd_name, is_found = self.transform_by_team(odd_name, self.name_a)
            team0 = "a" if is_found else ""

        for sibling in tag_i.next_siblings:
            team = team0
            if type(sibling) == element.Tag:
                lines = sibling.get_text("\n", strip=True).splitlines()
                if len(lines) > 1:
                    suffix = lines[0]
                    param, is_yes_no = self.clear_yes_no(suffix)
                    search_obj_1 = name_pattern1.search(odd_name)
                    if is_yes_no:
                        suffix = param
                        self.add_odd(odd_name, lines[1], team=team, param=suffix, value_type=match_stat)
                    elif search_obj_1:
                        #Total Goals 2,5 / Both teams to score
                        param         = search_obj_1[1].replace(",",".")
                        odd_name_real = re.sub(r"[0-9.,]+", "", odd_name) #remove param from name
                        odd_name_real = " ".join(odd_name_real.split())   #remove double spaces
                        suffix        = re.sub(r"[0-9., ]+", "", suffix)
                        if suffix: odd_name_real = odd_name_real + " " + suffix
                        self.add_odd(odd_name_real, lines[1], param=param, value_type=match_stat)
                    elif odd_name.lower().find("correct score") >= 0:
                        is_swap = (suffix.find(self.name_a) >= 0)
                        scores0  = score_pattern.findall(suffix)
                        if is_swap:
                            scores = [s[1]+":"+s[0] for s in scores0]
                        else:
                            scores = [s[0]+":"+s[1] for s in scores0]
                        param = ",".join(scores)
                        self.add_odd(odd_name, lines[1], team=team, param=param, value_type=match_stat)
                    elif odd_name == "1st Half Result / 2nd Half Result":
                        search_obj = param_pattern.search(suffix)
                        if search_obj:
                            params_in = [search_obj[1].strip(),search_obj[2].strip()]
                            params_out = []
                            for p in params_in:
                                if p.find(self.name_h) >=0: p_out = "1"
                                elif p.find(self.name_a) >=0: p_out = "2"
                                elif p == "Draw": p_out = "X"
                                else: p_out = ""
                                params_out.append(p_out)
                            param = "/".join(params_out)
                            self.add_odd(odd_name, lines[1], param=param, value_type=match_stat)
                    elif odd_name.startswith("Match result / Total match goals"):
                        odd_name = odd_name.replace(",",".")
                        search_obj = param_pattern.search(suffix) #Tottenham or draw / over
                        suffix = search_obj[1].strip()
                        suffix, is_found = self.transform_by_team(suffix, self.name_h)
                        if is_found:
                            team = "h"
                        else:
                            suffix, is_found = self.transform_by_team(suffix, self.name_a)
                            team = "a"
                        if suffix and not suffix.startswith(" "): suffix = " " + suffix
                        suffix = " win" + suffix + " " + search_obj[2].strip()
                        self.add_odd(odd_name+suffix, lines[1], team=team, value_type=match_stat)
                    elif odd_name == "Match result and both teams to score":
                        if suffix.find(self.name_h) >=0: param = "w"
                        elif suffix.find(self.name_a) >=0: param = "l"
                        elif suffix.find("draw") >=0: param = "d"
                        else: param = ""
                        if param:
                            self.add_odd(odd_name, lines[1], param=param, value_type=match_stat)
                    elif odd_name == "Win No Bet":
                        if suffix.lower().find("win") >=0: param = "w"
                        elif suffix.lower().find("draw") >=0: param = "d"
                        else: param = ""
                        if param:
                            self.add_odd(odd_name, lines[1], param=param, team=team, value_type=match_stat)
                    else:
                        suffix_h, is_found_h = self.transform_by_team(suffix, self.name_h)
                        suffix_a, is_found_a = self.transform_by_team(suffix, self.name_a)
                        param = None
                        if odd_name.endswith("Minutes Betting"):
                            if is_found_h:
                                suffix = suffix_h
                            elif is_found_a:
                                suffix = "lose"
                        else:
                            if is_found_h and is_found_a:
                                suffix = "both"
                                team = team0
                            elif is_found_h:
                                team = "h"
                                suffix = suffix_h
                            elif is_found_a:
                                team = "a"
                                suffix = suffix_a
                            else:
                                team = team0
                        #
                        search_obj = over_under_pattern.search(suffix)
                        if search_obj:
                            param  = search_obj[2]
                            suffix = suffix.replace(param,"")
                            suffix = " ".join(suffix.split())  #remove double spaces and strip()
                            param  = param.replace(",",".")
                        if suffix: odd_name_real = odd_name + " " + suffix
                        else: odd_name_real = odd_name
                        self.add_odd(odd_name_real, lines[1], param=param, team=team, value_type=match_stat)


    def clear_yes_no(self, param):
        p = param.lower().replace("yes","1").replace("no","0").replace(" ","")
        if p in("0/0","0/1","1/0","1/1"):
            param = p.replace("/","\\")
            is_yes_no = 1
        else:
            is_yes_no = 0
        return param, is_yes_no



    def add_odd(self, odd_name, odd_value, param=None, team=None, value_type=None):
        
        odd_params = self.get_config(odd_name)
        # odd_params = PARIMATCH_ODDS.get(odd_name, None)
        if odd_params:
            value_type_real = odd_params.value_type
            period = odd_params.period
            if not period: period = 0
            if not value_type_real: value_type_real = value_type
            bet_type_slug = odd_params.bet_type.slug
            
            team = team if team else odd_params.team            
            param = param if param else odd_params.param

            # logger.debug("Add odd %s bet_type:%s team:%s period:%s param:%s" %(odd_name, bet_type_slug, team, period, param))
            odd = {
                        "bet_type":bet_type_slug, 
                        "odd_value":odd_value, 
                        "team": team, 
                        "period":period, 
                        "param":param, 
                        "yes":odd_params.yes, 
                        "value_type": ValueType.MAIN if not value_type_real else PARIMATCH_VALUE_TYPES[value_type_real],
                        "odd_bookie_config":odd_params,
                    }

            self.odds.append(odd)


    def _get_teams(self, teams_tag, is_football_stats):
        lines = teams_tag.get_text("\n", strip=True).splitlines()
        name_h      = lines[len(lines)-2]
        name_a      = lines[len(lines)-1]
        if is_football_stats:
            match_stat  = None
        else:
            match_stat  = "main"
        for key in PARIMATCH_STATS.keys():
            if name_h.startswith(key):
                name_h      = name_h[len(key):].strip()
                name_a      = name_a[len(key):].strip()
                match_stat  = PARIMATCH_STATS[key]
        return name_h, name_a, match_stat


    def transform_by_team(self, odd_name, team_name):
        if odd_name.find(team_name) >= 0:
            is_found = 1
            odd_name = odd_name.replace(team_name, "")
        else:
            is_found = 0
        odd_name = " ".join(odd_name.split())
        return odd_name, is_found


    def get_bs4_str(self, tag):
        if type(tag) == element.Tag:
            ret = tag.get_text().strip()
        else:
            ret = str(tag)
        return ret


    def get_td(self, tds, cnt):
        """ get td tag using attribute colspan

            Arguments:
            tds - list td tags (<td>..<\td><td>..<\td>...)
            cnt - tag number 
        """
        i = 0
        td_tag = None
        for td in tds:
            if i == cnt:
                td_tag = td
                break
            colspan = td.get("colspan")
            if colspan is None:
                i += 1
            else:
                i += int(colspan)
            if i > cnt:
                break
        return td_tag




