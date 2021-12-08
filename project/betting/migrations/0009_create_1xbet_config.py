# Generated by Django 2.2.1 on 2020-01-07 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0008_auto_20200108_1202'),
    ]

    def create_1xbet_config(apps, schema_editor):
        from ..models import BetType as BType
        # from core.models import LoadSource
        # from betting.models import OddBookieConfig
        BetType = apps.get_model("betting", "BetType")
        LoadSource = apps.get_model("core", "LoadSource")
        OddBookieConfig = apps.get_model("betting", "OddBookieConfig")

        XBET_ODDS = {
			  '1':    {'odd_name':'1', 'type':BType.WDL, 'period':'0', 'param':'w', 'team':'', 'yes':1},
			  'X':    {'odd_name':'X', 'type':BType.WDL, 'period':'0', 'param':'d', 'team':'', 'yes':1},
			  '2':    {'odd_name':'2', 'type':BType.WDL, 'period':'0', 'param':'l', 'team':'', 'yes':1},
			  '1X':   {'odd_name':'1X','type':BType.WDL, 'period':'0', 'param':'wd', 'team':'', 'yes':1},
			  '12':   {'odd_name':'12','type':BType.WDL, 'period':'0', 'param':'wl', 'team':'', 'yes':1},
			  '2X':   {'odd_name':'2X','type':BType.WDL, 'period':'0', 'param':'dl', 'team':'', 'yes':1},
			  'Total_O': {'odd_name':'Total Over','type':BType.TOTAL_OVER, 'period':'0', 'param':'', 'team':'', 'yes':1},
			  'Total_U': {'odd_name':'Total Under','type':BType.TOTAL_UNDER, 'period':'0', 'param':'', 'team':'', 'yes':1},
			  'IT1_O':   {'odd_name':'Individual Total Over','type':BType.TOTAL_OVER, 'period':'0', 'param':'', 'team':'h', 'yes':1},
			  'IT1_U':   {'odd_name':'Individual Total Under','type':BType.TOTAL_UNDER, 'period':'0', 'param':'', 'team':'h', 'yes':1},
			  'IT2_O':   {'odd_name':'Individual Total Over','type':BType.TOTAL_OVER, 'period':'0', 'param':'', 'team':'a', 'yes':1},
			  'IT2_U':   {'odd_name':'Individual Total Under','type':BType.TOTAL_UNDER, 'period':'0', 'param':'', 'team':'a', 'yes':1},
			  'Handicap_1':   {'odd_name':'Handicap','type':BType.HANDICAP, 'period':'0', 'param':'', 'team':'h', 'yes':1},
			  'Handicap_2':   {'odd_name':'Handicap','type':BType.HANDICAP, 'period':'0', 'param':'', 'team':'a', 'yes':1},

			  'G=1':   {'odd_name':'1x2','period':'0','param':'','team':'','yes':1,'handler':'add_wdl'},
			  'G=2':   {'odd_name':'Handicap','period':'0','param':'','team':'','yes':1,'handler':'add_handicap'},
			  'G=8':   {'odd_name':'Double Chance','period':'0','param':'','team':'','yes':1,'handler':'add_wdl'},
			  'G=9':   {'odd_name':'Draw.Score Draw','period':'0','param':'','team':'','yes':1,'handler':'add_wdl'},
			  'G=11':  {'odd_name':'HT-FT','type':BType.RESULT_HALF1_FULL,'period':'0','param':'','team':'','yes':1,'handler':'add_HT_FT'},
			  'G=12':  {'odd_name':'Goal Interval - Yes','type':BType.TOTAL_OVER_MINUTES,'period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=13':  {'odd_name':'Goal Interval - No','type':BType.TOTAL_UNDER_MINUTES,'period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=14':  {'odd_name':'Even/Odd','type':BType.TOTAL_EVEN_ODD,'period':'0','param':'','team':'','yes':1,'handler':'add_even_odd'},
			  'G=15':  {'odd_name':'Total 1','period':'0','param':'','team':'h','yes':1,'handler':'add_total'},
			  'G=17':  {'odd_name':'Total','period':'0','param':'','team':'','yes':1,'handler':'add_total'},
			  'G=18':  {'odd_name':'Scores In Each Half','period':'0','param':'','team':'','yes':1,'handler':'add_highest_half'},
			  'G=19':  {'odd_name':'Both Teams To Score','period':'0','param':'','team':'','yes':1,'handler':'add_both_team_to_score'},
			  'G=29':  {'odd_name':'Individual Total Interval - 1. Cards. Stats','type':BType.TOTAL,'period':'0','param':'','team':'h','yes':1,'handler':'add_exact_total'},
			  'G=30':  {'odd_name':'Individual Total Interval - 2. Cards. Stats','type':BType.TOTAL,'period':'0','param':'','team':'a','yes':1,'handler':'add_exact_total'},
			  'G=32':  {'odd_name':'Goal In Both Halves','period':'0','param':'0.5','team':'','yes':1,'handler':'add_both_halves_over'},
			  'G=60':  {'odd_name':'Race To','period':'0','param':'','team':'','yes':1,'handler':'add_race_to_goals'},
			  'G=62':  {'odd_name':'Total 2','period':'0','param':'','team':'a','yes':1,'handler':'add_total'},
			  'G=71':  {'odd_name':'Half/Half','type':BType.RESULT_HALF1_HALF2,'period':'0','param':'','team':'','yes':1,'handler':'add_HT_FT'},
			  'G=75':  {'odd_name':'Goal In Half','period':'0','param':'','team':'','yes':1,'handler':'add_half_to_score_first_goal'},
			  'G=91':  {'odd_name':'Individual Total 1 Even/Odd','type':BType.TOTAL_EVEN_ODD,'period':'0','param':'','team':'h','yes':1,'handler':'add_even_odd'},
			  'G=92':  {'odd_name':'Individual Total 2 Even/Odd','type':BType.TOTAL_EVEN_ODD,'period':'0','param':'','team':'a','yes':1,'handler':'add_even_odd'},
			  'G=99':  {'odd_name':'Asian Total','period':'0','param':'','team':'','yes':1,'handler':'add_total'},
			  'G=136': {'odd_name':'Correct Score','period':'0','param':'','team':'','yes':1,'handler':'add_correct_score'},
			  'G=275': {'odd_name':'Any Team To Win By','type':BType.MARGIN,'period':'0','param':'','team':'','yes':1,'handler':'add_margin'},
			  'G=285': {'odd_name':'Total Each Team Will Score Under/Over','period':'0','param':'','team':'','yes':1,'handler':'add_total'},
			  'G=303': {'odd_name':'Result In Minute','period':'0','param':'','team':'','yes':1,'handler':'add_wdl'},
			  'G=307': {'odd_name':'Handicap In Minute','period':'0','param':'','team':'','yes':1,'handler':'add_handicap'},
			  'G=852': {'odd_name':'Win To Nil','period':'0','param':'','team':'','yes':1,'handler':'add_result_teams_to_score'},
			  'G=864': {'odd_name':'Win By','type':BType.MARGIN,'period':'0','param':'','team':'','yes':1,'handler':'add_margin'},
			  'G=880': {'odd_name':'Result And Both Teams To Score','period':'0','param':'','team':'','yes':1,'handler':'add_wdl'},
			  'G=883': {'odd_name':'Fouls.Penalty Awarded','period':'0','param':'0.5','team':'','yes':1,'value_type':'penalty','handler':'add_total'},
			  'G=887': {'odd_name':'Goal In Time Interval - Yes/No','period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=893': {'odd_name':'Team Goal In Both Halves','period':'0','param':'','team':'','yes':1,'handler':'add_total'},
			  'G=899': {'odd_name':'To Win By Exactly One Goal Or To Draw','type':BType.MARGIN,'period':'0','param':'','team':'','yes':1,'handler':'add_margin'},
			  'G=901': {'odd_name':'Total Goals By Halves','period':'0','param':'','team':'','yes':1,'handler':'add_both_halves_over'},
			  'G=1130':{'odd_name':'Total Goals In Interval','type':BType.TOTAL,'period':'0','param':'','team':'','yes':1,'handler':'add_exact_total'},
			  'G=1140':{'odd_name':'Total Interval.. Cards. Stats','type':BType.TOTAL,'period':'0','param':'','team':'','yes':1,'handler':'add_exact_total'},
			  'G=1154':{'odd_name':'Results. Halves','period':'0','param':'','team':'','yes':1,'handler':'add_result_halves'},
			  'G=2280':{'odd_name':'Result / Teams To Score','period':'0','param':'','team':'','yes':1,'handler':'add_result_teams_to_score'},
			  'G=2402':{'odd_name':'Any Player To Get Booked During The Match. Cards. Stats','type':BType.TOTAL_OVER_MINUTES,'period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=2404':{'odd_name':'Team 1 Total In Interval. Cards. Stats','type':BType.TOTAL_OVER_MINUTES,'period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=2406':{'odd_name':'Team 2 Total In Interval. Cards. Stats','type':BType.TOTAL_OVER_MINUTES,'period':'0','param':'','team':'','yes':1,'handler':'add_goal_interval'},
			  'G=2422':{'odd_name':'Team 1 Scores In Halves','period':'0','param':'','team':'h','yes':1,'handler':'add_highest_half'},
			  'G=2424':{'odd_name':'Team 2 Scores In Halves','period':'0','param':'','team':'a','yes':1,'handler':'add_highest_half'},
			  'G=2444':{'odd_name':'Total And Both To Score','period':'0','param':'','team':'','yes':1,'handler':'add_both_team_to_score'},
			  'G=2446':{'odd_name':'Both Teams To Score In Halves','period':'0','param':'','team':'','yes':1,'handler':'add_both_team_to_score_in_halves'},
			  'G=2456':{'odd_name':'Team 1, First Goal In Interval','type':BType.TIME_TO_SCORE_FIRST_GOAL,'period':'0','param':'','team':'h','yes':1,'handler':'add_first_goal_interval'},
			  'G=2458':{'odd_name':'Team 2, First Goal In Interval','type':BType.TIME_TO_SCORE_FIRST_GOAL,'period':'0','param':'','team':'a','yes':1,'handler':'add_first_goal_interval'},
			  'G=2663':{'odd_name':'Team 1, Result + Total','period':'0','param':'','team':'h','yes':1,'handler':'add_result_and_total'},
			  'G=2665':{'odd_name':'Team 2, Result + Total','period':'0','param':'','team':'a','yes':1,'handler':'add_result_and_total'},
			  'G=2851':{'odd_name':'Both Teams To Score Yes/No + Total','period':'0','param':'','team':'','yes':1,'handler':'add_both_team_to_score'},
			  'G=2854':{'odd_name':'Asian Handicap','period':'0','param':'','team':'','yes':1,'handler':'add_handicap'},
			  'G=2866':{'odd_name':'Team 1 Win To Nil','period':'0','param':'','team':'','yes':1,'handler':'add_result_teams_to_score'},
			  'G=2867':{'odd_name':'Team 2 Win To Nil','period':'0','param':'','team':'','yes':1,'handler':'add_result_teams_to_score'},
			  'G=2876':{'odd_name':'Team 1 To Score N Goals','type':BType.TOTAL,'period':'0','param':'','team':'h','yes':1,'handler':'add_exact_total'},
			  'G=2878':{'odd_name':'Team 2 To Score N Goals','type':BType.TOTAL,'period':'0','param':'','team':'a','yes':1,'handler':'add_exact_total'},
			  'G=2987':{'odd_name':'W1 + Total 1','period':'0','param':'','team':'h','yes':1,'handler':'add_result_and_total'},
			  'G=2989':{'odd_name':'W2 + Total 2','period':'0','param':'','team':'a','yes':1,'handler':'add_result_and_total'},
			  'G=3005':{'odd_name':'Outcome + Number Of Goals','period':'0','param':'','team':'','yes':1,'handler':'add_result_and_total'},
			  'G=3307':{'odd_name':'Exact Number Of Goals','type':BType.TOTAL,'period':'0','param':'','team':'','yes':1,'handler':'add_exact_total'},
			  'G=3309':{'odd_name':'Individual Total 1 Exact Number Of Goals','type':BType.TOTAL,'period':'0','param':'','team':'h','yes':1,'handler':'add_exact_total'},
			  'G=3311':{'odd_name':'Individual Total 2 Exact Number Of Goals','type':BType.TOTAL,'period':'0','param':'','team':'a','yes':1,'handler':'add_exact_total'},
			  'G=8931':{'odd_name':'At Least One Team Will Score','period':'0','param':'','team':'','yes':1,'handler':'add_total'},
			  'G=9428':{'odd_name':'Double Chance + Team 1 Total','period':'0','param':'','team':'h','yes':1,'handler':'add_result_and_total'},
			  'G=9429':{'odd_name':'Double Chance + Team 2 Total','period':'0','param':'','team':'a','yes':1,'handler':'add_result_and_total'},
        }
        xbet = LoadSource.objects.get(slug='1xbet')
        
        OddBookieConfig.objects.filter(bookie = xbet).delete()

        for key in XBET_ODDS.keys():
            period = XBET_ODDS[key].get("period",None)
            if period:
                period = int(period)
            else:
                period = None
            bet_type_slug = XBET_ODDS[key].get("type","")
            if bet_type_slug:
            	bet_type = BetType.objects.get(slug=bet_type_slug)
            else:
            	bet_type = None
            odd = OddBookieConfig(
                bookie = xbet,
                code = key,
                name = key,
                bet_type = bet_type,
                period = period,
                param = XBET_ODDS[key].get("param",""),
                team = XBET_ODDS[key].get("team",""),
                yes = XBET_ODDS[key].get("yes",""),
                bookie_handler = XBET_ODDS[key].get("handler",""),
                value_type = XBET_ODDS[key].get("value_type",""),
                )
            odd.save()



    operations = [
        migrations.RunPython(create_1xbet_config),
    ]