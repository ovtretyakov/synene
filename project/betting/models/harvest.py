import traceback
from decimal import Decimal
import logging
import math

from django.db import models
from django.utils import timezone
from django.db import connection

from .forecast import Harvest, HarvestGroup, HarvestHandler
from project.core.models import Match, Team, Season, MatchStats

logger = logging.getLogger(__name__)


class TeamSkill(models.Model):

    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    harvest_group = models.ForeignKey(HarvestGroup, on_delete=models.CASCADE, verbose_name='Harvest Group')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Team')
    event_date = models.DateField('Event date')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    match_cnt = models.IntegerField('Match Count')

    # values for calculations (log format)
    lvalue1  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue2  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue3  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue4  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue5  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue6  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue7  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue8  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue9  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    lvalue10 = models.DecimalField('LValue1', max_digits=10, decimal_places=5)

    # values for presentation
    value1  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value2  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value3  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value4  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value5  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value6  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value7  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value8  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value9  = models.DecimalField('LValue1', max_digits=10, decimal_places=5)
    value10 = models.DecimalField('LValue1', max_digits=10, decimal_places=5)

    param = models.CharField('Param', max_length=20, default='0')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest','team','param','event_date','match'], name='unique_team_skill_harvest'),
        ]
        indexes = [
            models.Index(fields=['harvest_group','event_date'], name='team_skill_hgroup_edate_idx'),
        ]

    def __str__(self):
        return f'W:{self.harvest},T:{self.team},D:{self.event_date}'

    @classmethod
    def _get_team_skill(cls, harvest, team, skill_date, match=None, param="0"):
        team_skill = cls.objects.filter(harvest=harvest,team=team,param=param,event_date__lt=skill_date).order_by("-event_date").first()
        return team_skill

    @classmethod
    def get_empty(cls, harvest, team, skill_date, match=None, param="0"):
        obj = cls()
        obj.erase(harvest, team, skill_date, match, param=param)
        return obj

    @classmethod
    def _do_harvest(cls, harvest, harvest_group, match):
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    @classmethod
    def turn_data(cls, data1, data2, new_data, smooth_interval, delta_koef="2"):
        prev_data = data1 + data2
        new_data = math.log(new_data)
        delta = (Decimal(new_data)-Decimal(prev_data))/Decimal(delta_koef)
        alfa = Decimal("2")/(Decimal("1") + smooth_interval)
        new_data1 = alfa*(data1 + delta) + (Decimal("1")-alfa)*data1
        new_data2 = alfa*(data2 + delta) + (Decimal("1")-alfa)*data2
        return new_data1, new_data2


    @classmethod
    def get_handler_class(cls, harvest, handler=None):
        if not handler:
            harvest_handler = None
            try:
                harvest_handler = HarvestHandler.objects.get(harvest=harvest)
            except HarvestHandler.DoesNotExist:
                err_str = "Missing HarvestHandler for harvest=%s" % (harvest, )
                logger.error("!!!" + err_str) 
                raise ValueError(err_str)
            handler = harvest_handler.handler
        handler_cls = globals().get(handler)
        if not handler_cls: 
            err_str = 'Unknonwn harvest handler "%s" in %s' % (handler, harvest, )
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)
        return handler_cls

    @classmethod
    def get_team_skill(cls, harvest, team, skill_date, match=None, handler=None, param="0"):
        handler_cls = cls.get_handler_class(harvest, handler)
        return handler_cls._get_team_skill(harvest, team, skill_date, match, param=param)


    @classmethod
    def do_harvest(cls, harvest, harvest_group, match, config):
        handler_cls = cls.get_handler_class(harvest)
        return handler_cls._do_harvest(harvest, harvest_group, match, config)

    @classmethod
    def calculate_xg_mse(cls, harvest, start_date):
        with connection.cursor() as cursor:
            select_mse = """ 
            SELECT COUNT(*) AS cnt,
                   SQRT(AVG((xg_h - h)*(xg_h - h))) AS sma_h,
                   SQRT(AVG((xg_a - a)*(xg_a - a))) AS sma_a
              FROM 
                (
                  SELECT m.id AS match_id, sh.value::numeric AS xg_h, sa.value::numeric AS xg_a,
                         (SELECT value1
                              FROM
                              (
                                SELECT sh.value1, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) * 
                         (SELECT value2
                              FROM
                              (
                                SELECT sh.value2, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_a_id AND sh.param = 'a' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) AS h, 
                        (SELECT value1
                              FROM
                              (
                                SELECT sh.value1, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_a_id AND sh.param = 'a' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) * 
                         (SELECT value2
                              FROM
                              (
                                SELECT sh.value2, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) AS a       
                    FROM synene.core_match m, 
                         synene.core_matchstats sh, synene.core_matchstats sa
                    WHERE m.status = 'F' AND m.match_date >= %s
                      AND sh.match_id = m.id AND sh.stat_type = 'xg' AND sh.competitor = 'h' AND sh.period = %s
                      AND sa.match_id = m.id AND sa.stat_type = 'xg' AND sa.competitor = 'a' AND sa.period = %s
                ) d2
              WHERE d2.h IS NOT NULL AND d2.a IS NOT NULL
            """
            cursor.execute(select_mse, [harvest.pk, harvest.pk, harvest.pk, harvest.pk, start_date, harvest.period, harvest.period, ])
            row = cursor.fetchone()
        cnt = row[0]
        mse_h = row[1]
        mse_a = row[2]
        return cnt, mse_h, mse_a


    @classmethod
    def calculate_g_mse(cls, harvest, start_date):
        with connection.cursor() as cursor:
            select_mse = """ 
            SELECT COUNT(*) AS cnt,
                   SQRT(AVG((xg_h - h)*(xg_h - h))) AS sma_h,
                   SQRT(AVG((xg_a - a)*(xg_a - a))) AS sma_a
              FROM 
                (
                  SELECT m.id AS match_id, sh.value::numeric AS xg_h, sa.value::numeric AS xg_a,
                         (SELECT value9
                              FROM
                              (
                                SELECT sh.value9, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) * 
                         (SELECT value10
                              FROM
                              (
                                SELECT sh.value10, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_a_id AND sh.param = 'a' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) AS h, 
                        (SELECT value9
                              FROM
                              (
                                SELECT sh.value9, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_a_id AND sh.param = 'a' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) * 
                         (SELECT value10
                              FROM
                              (
                                SELECT sh.value10, row_number() OVER(ORDER BY event_date DESC) AS rn
                                       FROM synene.betting_teamskill sh
                                  WHERE sh.harvest_id = %s AND sh.team_id = m.team_h_id AND sh.param = 'h' AND sh.event_date < m.match_date
                              )dd WHERE rn = 1  
                         ) AS a       
                    FROM synene.core_match m, 
                         synene.core_matchstats sh, synene.core_matchstats sa
                    WHERE m.status = 'F' AND m.match_date >= %s
                      AND sh.match_id = m.id AND sh.stat_type = 'g' AND sh.competitor = 'h' AND sh.period = %s
                      AND sa.match_id = m.id AND sa.stat_type = 'g' AND sa.competitor = 'a' AND sa.period = %s
                ) d2
              WHERE d2.h IS NOT NULL AND d2.a IS NOT NULL
            """
            cursor.execute(select_mse, [harvest.pk, harvest.pk, harvest.pk, harvest.pk, start_date, harvest.period, harvest.period, ])
            row = cursor.fetchone()
        cnt = row[0]
        mse_h = row[1]
        mse_a = row[2]
        return cnt, mse_h, mse_a



    def erase(self, harvest=None, team=None, skill_date=None, match=None, param="0"):
        self.pk = None
        self.harvest = harvest
        self.harvest_group = None
        self.team = team
        self.event_date = skill_date
        self.param = param
        self.match = match
        self.match_cnt = 0
        self.lvalue1  = 0
        self.lvalue2  = 0
        self.lvalue3  = 0
        self.lvalue4  = 0
        self.lvalue5  = 0
        self.lvalue6  = 0
        self.lvalue7  = 0
        self.lvalue8  = 0
        self.lvalue9  = 0
        self.lvalue10 = 0
        self.value1  = 0
        self.value2  = 0
        self.value3  = 0
        self.value4  = 0
        self.value5  = 0
        self.value6  = 0
        self.value7  = 0
        self.value8  = 0
        self.value9  = 0
        self.value10 = 0


###################################################################
class xGHandler(TeamSkill):
    class Meta:
        proxy = True


    # lvalue1  - expected goals (logarithm)
    # lvalue2  - expected goals against (logarithm)
    # lvalue3  - koef real goals (logarithm)
    # lvalue4  - koef real goals against (logarithm)

    # value1  - expected goals
    # value2  - expected goals against
    # value3  - koef real goals
    # value4  - koef real goals against

    # value9  - expected goals (final)
    # value10 - expected goals against (final)

    @classmethod
    def _get_prev_season(cls, league, season):
        prev_season = (Season.objects.filter(league=league, 
                                             start_date__isnull=False, 
                                             start_date__lt=season.start_date)
                                    .order_by("-start_date")
                                    .first()
                      )
        return prev_season


    @classmethod
    def _get_initialteam_skill(cls, harvest, team, skill_date, match, season, league, param="0"):
        prev_season = cls._get_prev_season(league, season) 
        team_skill = cls.get_empty(harvest, team, skill_date, match, param=param)
        if prev_season:
            #get rusults of worst teams of previos season
            with connection.cursor() as cursor:
                select_prev_data = """ 
                    SELECT AVG(s3.lvalue1) AS lvalue1, AVG(s3.lvalue2) AS lvalue2, AVG(s3.lvalue3) AS lvalue3, AVG(s3.lvalue4) AS lvalue4
                      FROM 
                        (  
                        SELECT s2.lvalue1, s2.lvalue2, s2.lvalue3, s2.lvalue4,
                               row_number() OVER(ORDER BY s2.lvalue1) AS rn
                          FROM 
                            (  
                            SELECT s.*,
                                   row_number() OVER(PARTITION BY s.team_id ORDER BY event_date DESC) AS rn
                              FROM betting_teamskill  s
                              WHERE harvest_id = %s AND event_date BETWEEN %s AND %s AND param=%s
                             ) s2
                          WHERE s2.rn = 1
                        ) s3
                      WHERE s3.rn <= 2
                """
                cursor.execute(select_prev_data, [harvest.pk, prev_season.start_date, prev_season.end_date, param, ])
                row = cursor.fetchone()
                lvalue1 = row[0]
                lvalue2 = row[1]
                lvalue3 = row[2]
                lvalue4 = row[3]
                if lvalue1 != None:
                    team_skill.lvalue1 = lvalue1
                    team_skill.lvalue2 = lvalue2
                    team_skill.lvalue3 = lvalue3
                    team_skill.lvalue4 = lvalue4
        return team_skill


    @classmethod
    def _get_team_skill(cls, harvest, team, skill_date, match=None, param="0"):

        season = None
        league = None
        if match:
            season = match.season
            league = match.league

        team_skill = cls.objects.filter(harvest=harvest,team=team,param=param,event_date__lt=skill_date).order_by("-event_date").first()

        if team_skill:
            team_skill_season = team_skill.match.season
            if season and season.name != Season.UNKNOWN and season != team_skill_season:
                prev_season = cls._get_prev_season(league, season) 
                if team_skill_season != prev_season:
                    team_skill = cls._get_initialteam_skill(harvest, team, skill_date, match, season, league, param=param)
        else:
            if match:
                team_skill = cls._get_initialteam_skill(harvest, team, skill_date, match, season, league, param=param)
            else:
                team_skill = cls.get_empty(harvest, team, skill_date, param=param)

        return team_skill

    @classmethod
    def _do_harvest(cls, harvest, harvest_group, match, config):
        team_h = match.team_h
        team_a = match.team_a
        skill_h = cls._get_team_skill(harvest, team_h, match.match_date, match, param="h")
        skill_a = cls._get_team_skill(harvest, team_a, match.match_date, match, param="a")
        period = harvest.period

        smooth_interval = config.get("smooth-interval")
        deviation_smooth_interval = config.get("deviation-smooth-interval")
        zero_value = config.get("zero-value")
        deviation_zero_value = config.get("deviation-zero-value")
        delta_koef_h = config.get("delta-koef-h", "2.0")
        delta_koef_a = config.get("delta-koef-a", "2.0")
        deviation_delta_koef_h = config.get("deviation-delta-koef-h", "2.0")
        deviation_delta_koef_a = config.get("deviation-delta-koef-a", "2.0")

        if not smooth_interval:
            err_str = 'Missing config parameter "smooth-interval"'
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)
        if not deviation_smooth_interval:
            err_str = 'Missing config parameter "deviation-smooth-interval"'
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)
        if not zero_value:
            err_str = 'Missing config parameter "zero-value"'
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)
        if not deviation_zero_value:
            err_str = 'Missing config parameter "deviation-zero-value"'
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)

        smooth_interval = Decimal(smooth_interval)
        deviation_smooth_interval = Decimal(deviation_smooth_interval)
        zero_value = Decimal(zero_value)
        deviation_zero_value = Decimal(deviation_zero_value)

        stat_goal_h, stat_goal_a = match.get_competitors_values(Match.GOALS, period)
        if not stat_goal_h or not stat_goal_a:
            return
        goal_h = Decimal(stat_goal_h)    
        goal_a = Decimal(stat_goal_a)
        if goal_h == Decimal('0'):
            goal_h = Decimal(deviation_zero_value)
        if goal_a == Decimal('0'):
            goal_a = Decimal(deviation_zero_value)

        stat_xg_h, stat_xg_a = match.get_competitors_values(Match.XG, period)
        if not stat_xg_h or not stat_xg_a:
            return
        xg_h = Decimal(stat_xg_h)    
        xg_a = Decimal(stat_xg_a)    
        if xg_h == Decimal('0'):
            xg_h = Decimal(zero_value)
        if xg_a == Decimal('0'):
            xg_a = Decimal(zero_value)

        #xG
        skill_h.lvalue1, skill_a.lvalue2 = cls.turn_data(skill_h.lvalue1, skill_a.lvalue2, xg_h, smooth_interval, delta_koef_h)
        skill_a.lvalue1, skill_h.lvalue2 = cls.turn_data(skill_a.lvalue1, skill_h.lvalue2, xg_a, smooth_interval, delta_koef_a)

        #goal
        skill_h.lvalue3, skill_a.lvalue4 = cls.turn_data(skill_h.lvalue3, skill_a.lvalue4, goal_h/xg_h, 
                                                        deviation_smooth_interval, deviation_delta_koef_h)
        skill_a.lvalue3, skill_h.lvalue4 = cls.turn_data(skill_a.lvalue3, skill_h.lvalue4, goal_a/xg_a, 
                                                        deviation_smooth_interval, deviation_delta_koef_a)
     
        skill_h.value1 = math.exp(skill_h.lvalue1)
        skill_h.value2 = math.exp(skill_h.lvalue2)
        skill_h.value3 = math.exp(skill_h.lvalue3)
        skill_h.value4 = math.exp(skill_h.lvalue4)
        skill_h.value9  = skill_h.value1 * skill_h.value3
        skill_h.value10 = skill_h.value2 * skill_h.value4

        skill_a.value1 = math.exp(skill_a.lvalue1)
        skill_a.value2 = math.exp(skill_a.lvalue2)
        skill_a.value3 = math.exp(skill_a.lvalue3)
        skill_a.value4 = math.exp(skill_a.lvalue4)
        skill_a.value9  = skill_a.value1 * skill_a.value3
        skill_a.value10 = skill_a.value2 * skill_a.value4

        skill_h.match = match
        skill_a.match = match
        skill_h.event_date = match.match_date
        skill_a.event_date = match.match_date
        skill_h.harvest_group = harvest_group
        skill_a.harvest_group = harvest_group
        skill_h.match_cnt += 1
        skill_a.match_cnt += 1
        skill_h.pk = None
        skill_a.pk = None

        skill_h.save()
        skill_a.save()

