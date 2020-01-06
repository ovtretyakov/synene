# Generated by Django 2.2.1 on 2019-08-04 11:53

from django.db import migrations


class Migration(migrations.Migration):

    def create_parimatch_config(apps, schema_editor):
        from betting.models import BetType as BType
        # from core.models import LoadSource
        # from betting.models import OddBookieConfig
        BetType = apps.get_model("betting", "BetType")
        LoadSource = apps.get_model("core", "LoadSource")
        OddBookieConfig = apps.get_model("betting", "OddBookieConfig")

        PARIMATCH_ODDS = {
            "1":                          {"type":BType.WDL,         "period":"0", "param":"w",  "team":"", "yes":1},
            "X":                          {"type":BType.WDL,         "period":"0", "param":"d",  "team":"", "yes":1},
            "2":                          {"type":BType.WDL,         "period":"0", "param":"l",  "team":"", "yes":1},
            "1X":                         {"type":BType.WDL,         "period":"0", "param":"wd", "team":"", "yes":1},
            "12":                         {"type":BType.WDL,         "period":"0", "param":"wl", "team":"", "yes":1},
            "X2":                         {"type":BType.WDL,         "period":"0", "param":"dl", "team":"", "yes":1},
            "Hand":                       {"type":BType.HANDICAP,    "period":"0", "param":"",   "team":"", "yes":1},
            "Total_Over":                 {"type":BType.TOTAL_OVER,  "period":"0", "param":"",   "team":"", "yes":1},
            "Total_Under":                {"type":BType.TOTAL_UNDER, "period":"0", "param":"",   "team":"", "yes":1},
            "iTotal_Over":                {"type":BType.TOTAL_OVER,  "period":"0", "param":"",   "team":"", "yes":1},
            "iTotal_Under":               {"type":BType.TOTAL_UNDER, "period":"0", "param":"",   "team":"", "yes":1},
            "1-st half_1":                {"type":BType.WDL,         "period":"1", "param":"w",  "team":"", "yes":1},
            "1-st half_X":                {"type":BType.WDL,         "period":"1", "param":"d",  "team":"", "yes":1},
            "1-st half_2":                {"type":BType.WDL,         "period":"1", "param":"l",  "team":"", "yes":1},
            "1-st half_1X":               {"type":BType.WDL,         "period":"1", "param":"wd", "team":"", "yes":1},
            "1-st half_12":               {"type":BType.WDL,         "period":"1", "param":"wl", "team":"", "yes":1},
            "1-st half_X2":               {"type":BType.WDL,         "period":"1", "param":"dl", "team":"", "yes":1},
            "1-st half_Hand":             {"type":BType.HANDICAP,    "period":"1", "param":"",   "team":"", "yes":1},
            "1-st half_Total_Over":       {"type":BType.TOTAL_OVER,  "period":"1", "param":"",   "team":"", "yes":1},
            "1-st half_Total_Under":      {"type":BType.TOTAL_UNDER, "period":"1", "param":"",   "team":"", "yes":1},
            "1-st half_iTotal_Over":      {"type":BType.TOTAL_OVER,  "period":"1", "param":"",   "team":"", "yes":1},
            "1-st half_iTotal_Under":     {"type":BType.TOTAL_UNDER, "period":"1", "param":"",   "team":"", "yes":1},
            "2-nd half_1":                {"type":BType.WDL,         "period":"2", "param":"w",  "team":"", "yes":1},
            "2-nd half_X":                {"type":BType.WDL,         "period":"2", "param":"d",  "team":"", "yes":1},
            "2-nd half_2":                {"type":BType.WDL,         "period":"2", "param":"l",  "team":"", "yes":1},
            "2-nd half_1X":               {"type":BType.WDL,         "period":"2", "param":"wd", "team":"", "yes":1},
            "2-nd half_12":               {"type":BType.WDL,         "period":"2", "param":"wl", "team":"", "yes":1},
            "2-nd half_X2":               {"type":BType.WDL,         "period":"2", "param":"dl", "team":"", "yes":1},
            "2-nd half_Hand":             {"type":BType.HANDICAP,    "period":"2", "param":"",   "team":"", "yes":1},
            "2-nd half_Total_Over":       {"type":BType.TOTAL_OVER,  "period":"2", "param":"",   "team":"", "yes":1},
            "2-nd half_Total_Under":      {"type":BType.TOTAL_UNDER, "period":"2", "param":"",   "team":"", "yes":1},
            "2-nd half_iTotal_Over":      {"type":BType.TOTAL_OVER,  "period":"2", "param":"",   "team":"", "yes":1},
            "2-nd half_iTotal_Under":     {"type":BType.TOTAL_UNDER, "period":"2", "param":"",   "team":"", "yes":1},
            "1/1 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"1/1", "team":"", "yes":1},
            "1/X H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"1/X", "team":"", "yes":1},
            "1/2 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"1/2", "team":"", "yes":1},
            "X/1 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"X/1", "team":"", "yes":1},
            "X/X H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"X/X", "team":"", "yes":1},
            "X/2 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"X/2", "team":"", "yes":1},
            "2/1 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"2/1", "team":"", "yes":1},
            "2/X H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"2/X", "team":"", "yes":1},
            "2/2 H/F":                    {"type":BType.RESULT_HALF1_FULL, "period":"0", "param":"2/2", "team":"", "yes":1},
            "Goal in first half yes":     {"type":BType.TOTAL_OVER,  "period":"1", "param":"0.50","team":"", "yes":1},
            "Goal in first half no":      {"type":BType.TOTAL_UNDER, "period":"1", "param":"0.50","team":"", "yes":1},
            "Goal in second half yes":    {"type":BType.TOTAL_OVER,  "period":"2", "param":"0.50","team":"", "yes":1},
            "Goal in second half no":     {"type":BType.TOTAL_UNDER, "period":"2", "param":"0.50","team":"", "yes":1},
            "Goals both halves yes":      {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"0.50","team":"", "yes":1},
            "Goals both halves no":       {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"0.50","team":"", "yes":0},
            "Winning margin 1 goal yes":  {"type":BType.MARGIN,      "period":"0", "param":"1,","team":"", "yes":1},
            "Winning margin 1 goal no":   {"type":BType.MARGIN,      "period":"0", "param":"1,","team":"", "yes":0},
            "Winning margin 1 goal or draw yes":  {"type":BType.MARGIN, "period":"0", "param":"0,1,","team":"", "yes":1},
            "Winning margin 1 goal or draw no":   {"type":BType.MARGIN, "period":"0", "param":"0,1,","team":"", "yes":0},
            "wins and over 2.5 yes":       {"type":BType.W_AND_TOTAL_OVER,  "period":"0", "param":"2.50","team":"", "yes":1},
            "wins and under 2.5 yes":      {"type":BType.W_AND_TOTAL_UNDER, "period":"0", "param":"2.50","team":"", "yes":1},
            "won't lose and over 2.5 yes": {"type":BType.WD_AND_TOTAL_OVER, "period":"0", "param":"2.50","team":"", "yes":1},
            "won't lose and under 2.5 yes":{"type":BType.WD_AND_TOTAL_UNDER,"period":"0", "param":"2.50","team":"", "yes":1},
            "wins both halves yes":        {"type":BType.WIN_BOTH,    "period":"0", "param":"","team":"", "yes":1},
            "wins both halves no":         {"type":BType.WIN_BOTH,    "period":"0", "param":"","team":"", "yes":0},
            "wins at least one half yes":  {"type":BType.WIN_LEAST_ONE_HALF, "period":"0", "param":"","team":"", "yes":1},
            "wins at least one half no":   {"type":BType.WIN_LEAST_ONE_HALF, "period":"0", "param":"","team":"", "yes":0},
            "to win to nil yes":           {"type":BType.WIN_TO_NIL, "period":"0", "param":"","team":"", "yes":1},
            "to win to nil no":            {"type":BType.WIN_TO_NIL, "period":"0", "param":"","team":"", "yes":0},
            "Goal in match yes":           {"type":BType.TOTAL_OVER,  "period":"0", "param":"0.50", "team":"", "yes":1},
            "Goal in match no":            {"type":BType.TOTAL_UNDER, "period":"0", "param":"0.50", "team":"", "yes":1},
            "Correct score 1":             {"type":BType.CORRECT_SCORE, "period":"0", "param":"", "team":"", "yes":1},
            "Correct score X":             {"type":BType.CORRECT_SCORE, "period":"0", "param":"", "team":"", "yes":1},
            "Correct score 2":             {"type":BType.CORRECT_SCORE, "period":"0", "param":"", "team":"", "yes":1},
            "To score over 1,5 goals both":{"type":BType.ITOTAL_BOTH_OVER, "period":"0", "param":"1.50", "team":"", "yes":1},
            "To score over 1,5 goals only":{"type":BType.ITOTAL_ONLY_OVER, "period":"0", "param":"1.50", "team":"", "yes":1},
            "To score over 1,5 goals Neither Team":{"type":BType.ITOTAL_BOTH_UNDER, "period":"0", "param":"1.50", "team":"", "yes":1},
            "Both teams to score in 1st half & 2nd half both":{"type":BType.ITOTAL_BOTH_OVER_IN_BOTH_HALVES, "period":"0", "param":"0.50", "team":"", "yes":1},
            "Both teams to score in 1st half & 2nd half only":{"type":BType.ITOTAL_ONLY_OVER_IN_BOTH_HALVES, "period":"0", "param":"0.50", "team":"", "yes":1},
            "Both teams to score in 1st half & 2nd half Neither team":{"type":BType.ITOTAL_BOTH_UNDER_IN_BOTH_HALVES, "period":"0", "param":"0.50", "team":"", "yes":1},
            "Both teams to score at 1st half - 2nd half":{"type":BType.BOTH_TO_SCORE_AT_1_2, "period":"0", "param":"", "team":"", "yes":1},
            "Both teams to score and either team to win yes":{"type":BType.ITOTAL_BOTH_OVER_AND_EITHER_WIN, "period":"0", "param":"0.50", "team":"", "yes":1},
            "Both teams to score and either team to win no": {"type":BType.ITOTAL_BOTH_OVER_AND_EITHER_WIN, "period":"0", "param":"0.50", "team":"", "yes":0},
            "At least one team to score 2 or more goals yes": {"type":BType.ITOTAL_AT_LEAST_OVER, "period":"0", "param":"1.50", "team":"", "yes":1},
            "At least one team to score 2 or more goals no": {"type":BType.ITOTAL_AT_LEAST_UNDER, "period":"0", "param":"1.50", "team":"", "yes":1},
            "At least one team to score 3 or more goals yes": {"type":BType.ITOTAL_AT_LEAST_OVER, "period":"0", "param":"2.50", "team":"", "yes":1},
            "At least one team to score 3 or more goals no": {"type":BType.ITOTAL_AT_LEAST_UNDER, "period":"0", "param":"2.50", "team":"", "yes":1},
            "15 Minutes Betting win":  {"type":BType.WDL_MINUTE, "period":"15", "param":"w", "team":"", "yes":1},
            "15 Minutes Betting draw": {"type":BType.WDL_MINUTE, "period":"15", "param":"d", "team":"", "yes":1},
            "15 Minutes Betting lose": {"type":BType.WDL_MINUTE, "period":"15", "param":"l", "team":"", "yes":1},
            "30 Minutes Betting win":  {"type":BType.WDL_MINUTE, "period":"30", "param":"w", "team":"", "yes":1},
            "30 Minutes Betting draw": {"type":BType.WDL_MINUTE, "period":"30", "param":"d", "team":"", "yes":1},
            "30 Minutes Betting lose": {"type":BType.WDL_MINUTE, "period":"30", "param":"l", "team":"", "yes":1},
            "60 Minutes Betting win":  {"type":BType.WDL_MINUTE, "period":"60", "param":"w", "team":"", "yes":1},
            "60 Minutes Betting draw": {"type":BType.WDL_MINUTE, "period":"60", "param":"d", "team":"", "yes":1},
            "60 Minutes Betting lose": {"type":BType.WDL_MINUTE, "period":"60", "param":"l", "team":"", "yes":1},
            "75 Minutes Betting win":  {"type":BType.WDL_MINUTE, "period":"75", "param":"w", "team":"", "yes":1},
            "75 Minutes Betting draw": {"type":BType.WDL_MINUTE, "period":"75", "param":"d", "team":"", "yes":1},
            "75 Minutes Betting lose": {"type":BType.WDL_MINUTE, "period":"75", "param":"l", "team":"", "yes":1},
            "Goal to be scored from 1st till 15th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"15", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 1st till 15th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"15", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 16th till 30th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"30", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 16th till 30th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"30", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 31st minute till Half Time? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"45", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 31st minute till Half Time? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"45", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 46th till 60th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"60", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 46th till 60th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"60", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 61st to 75th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"75", "param":"0.50", "team":"", "yes":1},
            "Goal to be scored from 61st to 75th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"75", "param":"0.50", "team":"", "yes":1},
            "Goal after 74 minute yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"90", "param":"0.50", "team":"", "yes":1},
            "Goal after 74 minute no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"90", "param":"0.50", "team":"", "yes":1},
            "Goal - from 1st to 15th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"15", "param":"0.50", "team":"", "yes":1},
            "Goal - from 1st to 15th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"15", "param":"0.50", "team":"", "yes":1},
            "Goal - from 16th to 30th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"30", "param":"0.50", "team":"", "yes":1},
            "Goal - from 16th to 30th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"30", "param":"0.50", "team":"", "yes":1},
            "Goal - from 31st minute to Half Time? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"45", "param":"0.50", "team":"", "yes":1},
            "Goal - from 31st minute to Half Time? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"45", "param":"0.50", "team":"", "yes":1},
            "Goal - from 46th to 60th Minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"60", "param":"0.50", "team":"", "yes":1},
            "Goal - from 46th to 60th Minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"60", "param":"0.50", "team":"", "yes":1},
            "Goal - from 61st to 75th minute? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"75", "param":"0.50", "team":"", "yes":1},
            "Goal - from 61st to 75th minute? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"75", "param":"0.50", "team":"", "yes":1},
            "Goal - from 76th minute to Full Time? yes": {"type":BType.TOTAL_OVER_MINUTES, "period":"90", "param":"0.50", "team":"", "yes":1},
            "Goal - from 76th minute to Full Time? no":  {"type":BType.TOTAL_UNDER_MINUTES,"period":"90", "param":"0.50", "team":"", "yes":1},
            "Total even":                           {"type":BType.TOTAL_EVEN_ODD,"period":"0", "param":"even", "team":"", "yes":1},
            "Total odd":                            {"type":BType.TOTAL_EVEN_ODD,"period":"0", "param":"odd", "team":"", "yes":1},
            "1st Half Result / 2nd Half Result":    {"type":BType.RESULT_HALF1_HALF2,"period":"0", "param":"", "team":"", "yes":1},
            "Match result / Total match goals 3.5 win over":   {"type":BType.W_AND_TOTAL_OVER,  "period":"0", "param":"3.50","team":"", "yes":1},
            "Match result / Total match goals 3.5 win under":  {"type":BType.W_AND_TOTAL_UNDER, "period":"0", "param":"3.50","team":"", "yes":1},
            "Match result / Total match goals 3.5 win or draw over":   {"type":BType.WD_AND_TOTAL_OVER,  "period":"0", "param":"3.50","team":"", "yes":1},
            "Match result / Total match goals 3.5 win or draw under":  {"type":BType.WD_AND_TOTAL_UNDER, "period":"0", "param":"3.50","team":"", "yes":1},
            "Match result and both teams to score":  {"type":BType.WDL_AND_BOTH_TEAMS_SCORE, "period":"0", "param":"","team":"", "yes":1},
            "Total match goals none":                {"type":BType.TOTAL, "period":"0", "param":"0","team":"", "yes":1},
            "Total match goals one":                 {"type":BType.TOTAL, "period":"0", "param":"1","team":"", "yes":1},
            "Total match goals two":                 {"type":BType.TOTAL, "period":"0", "param":"2","team":"", "yes":1},
            "Total match goals three":               {"type":BType.TOTAL, "period":"0", "param":"3","team":"", "yes":1},
            "Total match goals four":                {"type":BType.TOTAL, "period":"0", "param":"4","team":"", "yes":1},
            "Total match goals five":                {"type":BType.TOTAL, "period":"0", "param":"5","team":"", "yes":1},
            "Total match goals six":                 {"type":BType.TOTAL, "period":"0", "param":"6","team":"", "yes":1},
            "Total match goals seven or more":       {"type":BType.TOTAL_OVER, "period":"0", "param":"6.50","team":"", "yes":1},
            "Total goals 0 goals":                   {"type":BType.TOTAL, "period":"0", "param":"0","team":"", "yes":1},
            "Total goals 1 goal":                    {"type":BType.TOTAL, "period":"0", "param":"1","team":"", "yes":1},
            "Total goals 2 goals":                   {"type":BType.TOTAL, "period":"0", "param":"2","team":"", "yes":1},
            "Total goals 3 goals":                   {"type":BType.TOTAL, "period":"0", "param":"3","team":"", "yes":1},
            "Total goals 4 or more goals":           {"type":BType.TOTAL_OVER, "period":"0", "param":"3.50","team":"", "yes":1},
            "At least one team to score 4 or more goals yes": {"type":BType.ITOTAL_AT_LEAST_OVER, "period":"0", "param":"3.50","team":"", "yes":1},
            "At least one team to score 4 or more goals no":  {"type":BType.ITOTAL_AT_LEAST_UNDER,"period":"0", "param":"3.50","team":"", "yes":1},
            "Correct Score (Multiscore)":            {"type":BType.CORRECT_SCORE, "period":"0", "param":"", "team":"", "yes":1},
            "Match result to win in 1 or 2 goals":   {"type":BType.MARGIN,        "period":"0", "param":"1,2,","team":"", "yes":1},
            "Race to 2 goals":                       {"type":BType.RACE_TO_GOALS, "period":"0", "param":"2","team":"", "yes":1},
            "Race to 3 goals":                       {"type":BType.RACE_TO_GOALS, "period":"0", "param":"3","team":"", "yes":1},
            "To score first in the 1st half":        {"type":BType.RACE_TO_GOALS, "period":"1", "param":"1","team":"", "yes":1},
            "To score first in the 1st half No Goal":{"type":BType.TOTAL_UNDER,   "period":"1", "param":"0.50","team":"", "yes":1},
            "To score first in the 2nd half":        {"type":BType.RACE_TO_GOALS, "period":"2", "param":"1","team":"", "yes":1},
            "To score first in the 2nd half No Goal":{"type":BType.TOTAL_UNDER,   "period":"2", "param":"0.50","team":"", "yes":1},
            "1st goal in the match to score":        {"type":BType.RACE_TO_GOALS, "period":"0", "param":"1","team":"", "yes":1},
            "1st goal in the match to score no goal":{"type":BType.TOTAL_UNDER,   "period":"0", "param":"0.50","team":"", "yes":1},
            "to score its first goal 1st half"      :{"type":BType.HALF_TO_SCORE_FIRST_GOAL, "period":"0", "param":"1","team":"", "yes":1},
            "to score its first goal 2nd half"      :{"type":BType.HALF_TO_SCORE_FIRST_GOAL, "period":"0", "param":"2","team":"", "yes":1},
            "Time of 1st goal 1 st to 15th minute"       :{"type":BType.TIME_TO_SCORE_FIRST_GOAL, "period":"0", "param":"15","team":"", "yes":1},
            "Time of 1st goal 16th to 30th minute"       :{"type":BType.TIME_TO_SCORE_FIRST_GOAL, "period":"0", "param":"30","team":"", "yes":1},
            "Time of 1st goal 31 st minute to half time" :{"type":BType.TIME_TO_SCORE_FIRST_GOAL, "period":"0", "param":"45","team":"", "yes":1},
            "Time of 1st goal 46th to full time"         :{"type":BType.HALF_TO_SCORE_FIRST_GOAL, "period":"0", "param":"2","team":"", "yes":1},
            "goals even":                           {"type":BType.TOTAL_EVEN_ODD,"period":"0", "param":"even", "team":"", "yes":1},
            "goals odd":                            {"type":BType.TOTAL_EVEN_ODD,"period":"0", "param":"odd", "team":"", "yes":1},
            "Total Goals / Both teams to score Over&Yes" :{"type":BType.BOTH_TO_SCORE_AND_TOTAL_OVER,"period":"0", "param":"", "team":"", "yes":1},
            "Total Goals / Both teams to score Over&No"  :{"type":BType.NOT_BOTH_TO_SCORE_AND_TOTAL_OVER,"period":"0", "param":"", "team":"", "yes":1},
            "Total Goals / Both teams to score Under&Yes":{"type":BType.BOTH_TO_SCORE_AND_TOTAL_UNDER,"period":"0", "param":"", "team":"", "yes":1},
            "Total Goals / Both teams to score Under&No" :{"type":BType.NOT_BOTH_TO_SCORE_AND_TOTAL_UNDER,"period":"0", "param":"", "team":"", "yes":1},
            "to score 1 or 2 goals yes"            :{"type":BType.TOTAL,"period":"0", "param":"1,2", "team":"", "yes":1},
            "to score 1 or 2 goals no"             :{"type":BType.TOTAL,"period":"0", "param":"1,2", "team":"", "yes":0},
            "to score 2 or 3 goals yes"            :{"type":BType.TOTAL,"period":"0", "param":"2,3", "team":"", "yes":1},
            "to score 2 or 3 goals no"             :{"type":BType.TOTAL,"period":"0", "param":"2,3", "team":"", "yes":0},
            "to score two consecutive goals yes"   :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"2", "team":"", "yes":1},
            "to score two consecutive goals no"   :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"2", "team":"", "yes":0},
            "At least one team to score 2 consecutive goals yes":{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"2", "team":"", "yes":1},
            "At least one team to score 2 consecutive goals no" :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"2", "team":"", "yes":0},
            "to score three consecutive goals yes"              :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"3", "team":"", "yes":1},
            "to score three consecutive goals no"               :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"3", "team":"", "yes":0},
            "At least one team to score 3 consecutive goals yes":{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"3", "team":"", "yes":1},
            "At least one team to score 3 consecutive goals no" :{"type":BType.CONSECUTIVE_GOALS,"period":"0", "param":"3", "team":"", "yes":0},
            "1st half total goals none":           {"type":BType.TOTAL_UNDER,"period":"1", "param":"0.50", "team":"", "yes":1},
            "1st half total goals one":            {"type":BType.TOTAL,"period":"1", "param":"1", "team":"", "yes":1},
            "1st half total goals two":            {"type":BType.TOTAL,"period":"1", "param":"2", "team":"", "yes":1},
            "1st half total goals three":          {"type":BType.TOTAL,"period":"1", "param":"3", "team":"", "yes":1},
            "1st half total goals four":           {"type":BType.TOTAL,"period":"1", "param":"4", "team":"", "yes":1},
            "1st half total goals five or more":   {"type":BType.TOTAL_OVER,"period":"1", "param":"4.50", "team":"", "yes":1},
            "2nd half total goals none":           {"type":BType.TOTAL_UNDER,"period":"2", "param":"0.50", "team":"", "yes":1},
            "2nd half total goals one":            {"type":BType.TOTAL,"period":"2", "param":"1", "team":"", "yes":1},
            "2nd half total goals two":            {"type":BType.TOTAL,"period":"2", "param":"2", "team":"", "yes":1},
            "2nd half total goals three":          {"type":BType.TOTAL,"period":"2", "param":"3", "team":"", "yes":1},
            "2nd half total goals four":           {"type":BType.TOTAL,"period":"2", "param":"4", "team":"", "yes":1},
            "2nd half total goals five or more":   {"type":BType.TOTAL_OVER,"period":"2", "param":"4.50", "team":"", "yes":1},
            "1st half number of goals none":       {"type":BType.TOTAL_UNDER,"period":"1", "param":"0.50", "team":"", "yes":1},
            "1st half number of goals one":        {"type":BType.TOTAL,"period":"1", "param":"1", "team":"", "yes":1},
            "1st half number of goals two":        {"type":BType.TOTAL,"period":"1", "param":"2", "team":"", "yes":1},
            "1st half number of goals three or more":{"type":BType.TOTAL_OVER,"period":"1", "param":"2.50", "team":"", "yes":1},
            "2nd half number of goals none":       {"type":BType.TOTAL_UNDER,"period":"2", "param":"0.50", "team":"", "yes":1},
            "2nd half number of goals one":        {"type":BType.TOTAL,"period":"2", "param":"1", "team":"", "yes":1},
            "2nd half number of goals two":        {"type":BType.TOTAL,"period":"2", "param":"2", "team":"", "yes":1},
            "2nd half number of goals three or more":{"type":BType.TOTAL_OVER,"period":"2", "param":"2.50", "team":"", "yes":1},
            "1st half total goals Even/Odd even":  {"type":BType.TOTAL_EVEN_ODD,"period":"1", "param":"even", "team":"", "yes":1},
            "1st half total goals Even/Odd odd":   {"type":BType.TOTAL_EVEN_ODD,"period":"1", "param":"odd", "team":"", "yes":1},
            "2nd half total goals Even/Odd even":  {"type":BType.TOTAL_EVEN_ODD,"period":"2", "param":"even", "team":"", "yes":1},
            "2nd half total goals Even/Odd odd":   {"type":BType.TOTAL_EVEN_ODD,"period":"2", "param":"odd", "team":"", "yes":1},
            "Draw in either half yes":             {"type":BType.DRAW_IN_EITHER_HALF,"period":"", "param":"", "team":"", "yes":1},
            "Draw in either half no":              {"type":BType.DRAW_IN_EITHER_HALF,"period":"", "param":"", "team":"", "yes":0},
            "Highest scoring half 1st half":       {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"1", "team":"", "yes":1},
            "Highest scoring half draw":           {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"d", "team":"", "yes":1},
            "Highest scoring half 2nd half":       {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"2", "team":"", "yes":1},
            "The half with more goals scored by 1st half":   {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"1", "team":"", "yes":1},
            "The half with more goals scored by Equal":      {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"d", "team":"", "yes":1},
            "The half with more goals scored by 2nd half":   {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"2", "team":"", "yes":1},
            "1st half correct score":             {"type":BType.CORRECT_SCORE, "period":"1", "param":"", "team":"", "yes":1},
            "2nd half correct score":             {"type":BType.CORRECT_SCORE, "period":"2", "param":"", "team":"", "yes":1},
            "Win No Bet":                         {"type":BType.WIN_NO_BET, "period":"", "param":"", "team":"", "yes":1},
            "to score yes":                       {"type":BType.TOTAL_OVER, "period":"", "param":"0.50", "team":"", "yes":1},
            "to score no":                        {"type":BType.TOTAL_UNDER, "period":"", "param":"0.50", "team":"", "yes":1},
            "Both to score yes":                  {"type":BType.ITOTAL_BOTH_OVER, "period":"", "param":"0.50", "team":"", "yes":1},
            "Both to score no":                   {"type":BType.ITOTAL_BOTH_OVER, "period":"", "param":"0.50", "team":"", "yes":0},
            "Total 0-1 goals":                    {"type":BType.TOTAL, "period":"0", "param":"0,1","team":"", "yes":1},
            "Total 2-3 goals":                    {"type":BType.TOTAL, "period":"0", "param":"2,3","team":"", "yes":1},
            "1 half score":                       {"type":BType.TOTAL_OVER, "period":"1", "param":"0.50","team":"", "yes":1},
            "1 half not score":                   {"type":BType.TOTAL_UNDER, "period":"1", "param":"0.50","team":"", "yes":1},
            "2 half score":                       {"type":BType.TOTAL_OVER, "period":"2", "param":"0.50","team":"", "yes":1},
            "2 half not score":                   {"type":BType.TOTAL_UNDER, "period":"2", "param":"0.50","team":"", "yes":1},
            "Both halves score":                  {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"0.50","team":"", "yes":1},
            "Both halves not score":              {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"0.50","team":"", "yes":0},
            "1-st half both to score":            {"type":BType.ITOTAL_BOTH_OVER, "period":"1", "param":"0.50", "team":"", "yes":1},
            "1-st half at least one not to score":{"type":BType.ITOTAL_AT_LEAST_UNDER, "period":"1", "param":"0.50", "team":"", "yes":1},
            "2-nd half both to score":            {"type":BType.ITOTAL_BOTH_OVER, "period":"2", "param":"0.50", "team":"", "yes":1},
            "2-nd half at least one not to score":{"type":BType.ITOTAL_AT_LEAST_UNDER, "period":"2", "param":"0.50", "team":"", "yes":1},
            "Both halves total over 1.5 yes":     {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"1.50","team":"", "yes":1},
            "Both halves total over 1.5 no":      {"type":BType.TOTAL_BOTH_HALVES_OVER, "period":"0", "param":"1.50","team":"", "yes":0},
            "Both halves total under 1.5 yes":    {"type":BType.TOTAL_BOTH_HALVES_UNDER, "period":"0", "param":"1.50","team":"", "yes":1},
            "Both halves total under 1.5 no":     {"type":BType.TOTAL_BOTH_HALVES_UNDER, "period":"0", "param":"1.50","team":"", "yes":0},
          #stats  
            "match stat will have a penalty yes": {"type":BType.TOTAL_OVER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"penalty"},
            "match stat will have a penalty no":  {"type":BType.TOTAL_UNDER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"penalty"},
            "match stat anytime red card yes":    {"type":BType.TOTAL_OVER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"r_card"},
            "match stat anytime red card no":     {"type":BType.TOTAL_UNDER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"r_card"},
            "Penalty yes":                        {"type":BType.TOTAL_OVER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"penalty"},
            "Penalty no":                         {"type":BType.TOTAL_UNDER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"penalty"},
            "Red card yes":                       {"type":BType.TOTAL_OVER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"r_card"},
            "Red card no":                        {"type":BType.TOTAL_UNDER, "period":"0", "param":"0.50","team":"", "yes":1, "value_type":"r_card"},
          #corn  
            "1 half. Team total corn. over":      {"type":BType.TOTAL_OVER, "period":"1", "param":"","team":"", "yes":1},
            "1 half. Team total corn. under":     {"type":BType.TOTAL_UNDER, "period":"1", "param":"","team":"", "yes":1},
            "2 half. Team total corn. over":      {"type":BType.TOTAL_OVER, "period":"2", "param":"","team":"", "yes":1},
            "2 half. Team total corn. under":     {"type":BType.TOTAL_UNDER, "period":"2", "param":"","team":"", "yes":1},
            "Half with the most number of corners 1st Half":     {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"1", "team":"", "yes":1},
            "Half with the most number of corners Equal Number": {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"d", "team":"", "yes":1},
            "Half with the most number of corners 2nd Half":     {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"2", "team":"", "yes":1},
          #y.card
            "1 half. Team total y.card over":      {"type":BType.TOTAL_OVER, "period":"1", "param":"","team":"", "yes":1},
            "1 half. Team total y.card under":     {"type":BType.TOTAL_UNDER, "period":"1", "param":"","team":"", "yes":1},
            "2 half. Team total y.card over":      {"type":BType.TOTAL_OVER, "period":"2", "param":"","team":"", "yes":1},
            "2 half. Team total y.card under":     {"type":BType.TOTAL_UNDER, "period":"2", "param":"","team":"", "yes":1},
            "Half with the most number of yellow cards 1st Half":     {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"1", "team":"", "yes":1},
            "Half with the most number of yellow cards Equal Number": {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"d", "team":"", "yes":1},
            "Half with the most number of yellow cards 2nd Half":     {"type":BType.HIGHEST_VALUE_HALF,"period":"", "param":"2", "team":"", "yes":1},
        }
        parimatch = LoadSource.objects.get(slug='parimatch')
        for key in PARIMATCH_ODDS.keys():
            period = PARIMATCH_ODDS[key].get("period",None)
            if period:
                period = int(period)
            else:
                period = None
            odd = OddBookieConfig(
                bookie = parimatch,
                code = key,
                name = key,
                bet_type = BetType.objects.get(slug=PARIMATCH_ODDS[key].get("type","")),
                period = period,
                param = PARIMATCH_ODDS[key].get("param",""),
                team = PARIMATCH_ODDS[key].get("team",""),
                yes = PARIMATCH_ODDS[key].get("yes",""),
                bookie_handler = PARIMATCH_ODDS[key].get("handler",""),
                )
            odd.save()


    dependencies = [
        ("betting", "0003_ceate_proxy_odd_models"),
    ]

    operations = [
        migrations.RunPython(create_parimatch_config),
    ]
