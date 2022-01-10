import traceback
from decimal import Decimal
import logging
import math

from django.db import models, transaction, connection
from django.utils import timezone
from django.db.models.query import RawQuerySet
from django.db.models import sql

from project.core.models import LoadSource
from project.load.models import ErrorLog

logger = logging.getLogger(__name__)


class Distribution(models.Model):

    slug = models.SlugField(unique=True)
    name = models.CharField("Name", max_length=255, blank=True)
    comment = models.CharField("Comment", max_length=2000, blank=True)
    gathering_handler = models.CharField("Gathering handler", max_length=255, blank=True)
    gathering_date = models.DateTimeField("Gathering date", null=True, blank=True)
    start_date = models.DateField("Start date", null=True, blank=True)
    end_date = models.DateField("End date", null=True, blank=True)
    interpolation = models.BooleanField('Interpolation')
    step = models.DecimalField('Step', max_digits=10, decimal_places=4)

    def __str__(self):
        return self.slug


    @classmethod
    def get_distribution_data(cls, slug, value, param="0", object_id=0):
        distribution = Distribution.objects.get(slug=slug)
        real_distribution = distribution.get_real_distribution()
        distribution_data = real_distribution.get_distribution_by_value(value, param, object_id)
        return distribution_data

    ##################################################################################
    # methods to implement

    def prepare_distribution_cursor(self, cursor, from_value, to_value):
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    def gathering(self):
        self.gathering_data()

    def get_distribution_by_value(self, value, param="0", object_id=0):
        half_step = Decimal(self.step/2)
        value = Decimal(value)
        value_floor = Decimal(math.floor(value/half_step)) * half_step
        value_ceil = value_floor + half_step

        distribution_data = {}
        if self.interpolation:
            distrib_floor = {r[0]:r[1] for r in DistributionData.objects.filter(ditribution=self,
                                                                                param=param,
                                                                                object_id=object_id,
                                                                                value=value_floor).values_list("result_value", "data")
                            }
            distrib_ceil = {r[0]:r[1] for r in DistributionData.objects.filter(ditribution=self,
                                                                                param=param,
                                                                                object_id=object_id,
                                                                                value=value_ceil).values_list("result_value", "data")
                            }
            for key in distrib_floor.keys():
                dvalue_floor = distrib_floor.get(key,0.0)
                dvalue_ceil = distrib_ceil.get(key,0.0)
                dvalue = (dvalue_floor+dvalue_ceil)/2
                distribution_data[key] = dvalue
            for key in distrib_ceil.keys():
                dvalue_floor = distribution_data.get(key,None)
                if dvalue_floor == None:
                    dvalue = distrib_ceil.get(key,0.0)/2
                    distribution_data[key] = dvalue
            value_sum = sum([distribution_data[key] for key in distribution_data.keys()])
            for key in distribution_data.keys():
                distribution_data[key] = distribution_data[key]/value_sum

        else:
            distrib_value = value_floor
            if value_ceil - value < value - value_floor:
                distrib_value = value_ceil
            qs = DistributionData.objects.filter(ditribution=self,param=param,object_id=object_id,value=distrib_value)
            distribution_data = {r[0]:r[1] for r in qs.values_list("result_value", "data")}

        return distribution_data

    ##################################################################################

    def get_real_distribution(self):
        handler = self.gathering_handler
        handler_cls = globals().get(handler)
        if not handler_cls: 
            err_str = 'Unknonwn gathering handler "%s"' % (handler,  )
            logger.error("!!!" + err_str) 
            raise ValueError(err_str)
        obj = handler_cls.objects.get(pk=self.pk)
        return obj

    def _gathering(self, start_date, end_date):
        obj = self.get_real_distribution()
        obj.gathering_date = timezone.now()
        obj.start_date = start_date
        obj.end_date = end_date
        obj.save()
        obj.gathering()


    def api_gathering(self, start_date, end_date):
        try:
            with transaction.atomic():
                self._gathering(start_date, end_date)
        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Forecasting Error"
            load_source = LoadSource.objects.get(slug=LoadSource.SRC_UNKNOWN)
            ErrorLog.objects.create(
                                load_source = load_source,
                                source_session = None,
                                error_text = error_text,
                                error_context = "",
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '',
                                match_name = '',
                                file_name = '',
                                source_detail = None)
            raise e

    def gathering_data(self, object_id=0):
        half_step = self.step/2
        DistributionData.objects.filter(ditribution=self).delete()

        for period in range(0,1):
            print(f"period {period}")

            with connection.cursor() as cursor:

                team="h"
                from_value = 0 - half_step
                to_value = from_value + self.step
                value = 0
                print("distribution h")
                for i in range(1,100):
                    self.prepare_distribution_cursor(cursor, from_value, to_value, team=team, period=period)
                    for row in cursor.fetchall():
                        exist_data = True
                        DistributionData.objects.create(
                                                    ditribution = self,
                                                    param = f"{period}{team}",
                                                    object_id = object_id,
                                                    value = value,
                                                    result_value = row[0],
                                                    data = row[1]
                                                    )

                    from_value = from_value + half_step
                    to_value = to_value + half_step
                    value = value + half_step

                team="a"
                from_value = 0 - half_step
                to_value = from_value + self.step
                value = 0
                print("distribution a")
                for i in range(1,100):
                    self.prepare_distribution_cursor(cursor, from_value, to_value, team=team, period=period)
                    for row in cursor.fetchall():
                        exist_data = True
                        DistributionData.objects.create(
                                                    ditribution = self,
                                                    param = f"{period}{team}",
                                                    object_id = object_id,
                                                    value = value,
                                                    result_value = row[0],
                                                    data = row[1]
                                                    )

                    from_value = from_value + half_step
                    to_value = to_value + half_step
                    value = value + half_step

                team="a"
                for value_h in range(0,6):
                    print(f"Distribution a{value_h}")
                    from_value = 0 - half_step
                    to_value = from_value + self.step
                    value = 0
                    for i in range(1,100):
                        self.prepare_distribution_cursor(cursor, from_value, to_value, team=team, period=period, value_h=value_h)
                        for row in cursor.fetchall():
                            exist_data = True
                            DistributionData.objects.create(
                                                        ditribution = self,
                                                        param = f"{period}{team}{value_h}",
                                                        object_id = object_id,
                                                        value = value,
                                                        result_value = row[0],
                                                        data = row[1]
                                                        )

                        from_value = from_value + half_step
                        to_value = to_value + half_step
                        value = value + half_step



class DistributionData(models.Model):

    ditribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, verbose_name='Distribution')
    param = models.CharField("Param", max_length=20, default="0")
    object_id = models.IntegerField('Object ID', default=0)
    value = models.DecimalField('Step', max_digits=10, decimal_places=4)
    result_value = models.IntegerField('Result value', default=0)
    data = models.FloatField('Data')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['ditribution','param','object_id','value','result_value',], name='unique_distribution_data'),
        ]

    def __str__(self):
        return f'{self.ditribution}:{self.param}:{self.object_id}:{self.value}:{self.result_value}:{self.data}'



###################################################################
class xGGathering(Distribution):
    class Meta:
        proxy = True

    def prepare_distribution_cursor(self, cursor, from_value, to_value, team="h", value_h=None, period=0):
        from .forecast import Harvest

        harvest_slug = "hg-0"
        harvest = Harvest.objects.get(slug=harvest_slug)
        harvest_pk = harvest.pk

        team_str = "h_v1*a_v2"
        g_value_field = "s1_value"
        if team == "a":
            team_str = "a_v1*h_v2"
            g_value_field = "s2_value"

        value_filter = ""
        if team == "a" and value_h != None:
            value_filter = f" AND s1_value = {value_h} "

        sql_select = f""" 
                    SELECT g_value, COUNT(*)/MAX(all_cnt) AS p, COUNT(*) AS cnt 
                      FROM 
                        (
                          SELECT {g_value_field} AS g_value,
                                 COUNT(*) OVER() + 0.0 AS all_cnt
                            FROM
                              (
                              SELECT d2.*, 
                                     sa.value1 AS a_v1, sa.value2 AS a_v2, sa.value9 AS a_v9, sa.value10 AS a_v10,
                                     row_number() OVER(PARTITION BY d2.match_id ORDER BY sa.event_date DESC, sa.match_id DESC)  AS rn_a
                                FROM
                                  (
                                  SELECT *
                                    FROM
                                      (
                                      SELECT m.id AS match_id, m.match_date, m.team_h_id, m.team_a_id, 
                                             TO_NUMBER(s1.value,'99999999.9999') AS s1_value,
                                             TO_NUMBER(s2.value,'99999999.9999') AS s2_value,
                                             gh.value AS xgh, ga.value AS xga,
                                             sh.value1 AS h_v1, sh.value2 AS h_v2, sh.value9 AS h_v9, sh.value10 AS h_v10,
                                             row_number() OVER(PARTITION BY m.id ORDER BY sh.event_date DESC, sh.match_id DESC)  AS rn_h
                                        FROM core_match m
                                             JOIN core_matchstats s1 
                                               ON(s1.stat_type = 'g' AND s1.period = {period} AND s1.match_id = m.id AND s1.competitor = 'h' )
                                             JOIN core_matchstats s2 
                                               ON(s2.stat_type = 'g' AND s2.period = {period} AND s2.match_id = m.id AND s2.competitor = 'a')
                                             JOIN core_matchstats gh
                                               ON(gh.stat_type = 'xg' AND gh.period = {period} AND gh.match_id = m.id AND gh.competitor = 'h')
                                             JOIN core_matchstats ga 
                                               ON(ga.stat_type = 'xg' AND ga.period = {period} AND ga.match_id = m.id AND ga.competitor = 'a')
                                             JOIN betting_teamskill sh
                                               ON(sh.harvest_id = {harvest_pk} AND sh.team_id = m.team_h_id AND sh.param = 'h' AND 
                                                  sh.event_date < m.match_date AND sh.match_cnt > 3)
                                        WHERE  m.status = 'F'
                                          AND m.match_date BETWEEN %s AND %s
                                      ) d
                                    WHERE rn_h = 1
                                  ) d2
                                 JOIN betting_teamskill sa
                                   ON(sa.harvest_id = {harvest_pk} AND sa.team_id = d2.team_a_id AND sa.param = 'a' AND 
                                      sa.event_date < d2.match_date AND sa.match_cnt > 3)
                                WHERE rn_h = 1
                              ) d3
                            WHERE rn_a = 1
                              AND {team_str} >= %s AND {team_str} < %s
                              {value_filter}
                        ) d4
                      GROUP BY g_value
        """
        cursor.execute(sql_select, 
                              [self.start_date, self.end_date,
                               from_value, to_value,
                               ]
                             )


###################################################################
class xGGatheringHStd0(Distribution):
    class Meta:
        proxy = True

    def prepare_distribution_cursor(self, cursor, from_value, to_value, team="h", value_h=None, period=0):
        from .forecast import Harvest

        harvest_slug = f"hg-{period}"
        harvest = Harvest.objects.get(slug=harvest_slug)
        harvest_pk = harvest.pk

        team_str = "h_v9*a_v10"
        g_value_field = "s1_value"
        if team == "a":
            team_str = "a_v9*h_v10"
            g_value_field = "s2_value"

        value_filter = ""
        if team == "a" and value_h != None:
            value_filter = f" AND s1_value = {value_h} "

        sql_select = f""" 
                    SELECT g_value, COUNT(*)/MAX(all_cnt) AS p, COUNT(*) AS cnt 
                      FROM 
                        (
                          SELECT {g_value_field} AS g_value,
                                 COUNT(*) OVER() + 0.0 AS all_cnt
                            FROM
                              (
                              SELECT d2.*, 
                                     sa.value1 AS a_v1, sa.value2 AS a_v2, sa.value9 AS a_v9, sa.value10 AS a_v10,
                                     row_number() OVER(PARTITION BY d2.match_id ORDER BY sa.event_date DESC, sa.match_id DESC)  AS rn_a
                                FROM
                                  (
                                  SELECT *
                                    FROM
                                      (
                                      SELECT m.id AS match_id, m.match_date, m.team_h_id, m.team_a_id, 
                                             TO_NUMBER(s1.value,'99999999.9999') AS s1_value,
                                             TO_NUMBER(s2.value,'99999999.9999') AS s2_value,
                                             gh.value AS xgh, ga.value AS xga,
                                             sh.value1 AS h_v1, sh.value2 AS h_v2, sh.value9 AS h_v9, sh.value10 AS h_v10,
                                             row_number() OVER(PARTITION BY m.id ORDER BY sh.event_date DESC, sh.match_id DESC)  AS rn_h
                                        FROM core_match m
                                             JOIN core_matchstats s1 
                                               ON(s1.stat_type = 'g' AND s1.period = {period} AND s1.match_id = m.id AND s1.competitor = 'h' )
                                             JOIN core_matchstats s2 
                                               ON(s2.stat_type = 'g' AND s2.period = {period} AND s2.match_id = m.id AND s2.competitor = 'a')
                                             JOIN core_matchstats gh
                                               ON(gh.stat_type = 'xg' AND gh.period = {period} AND gh.match_id = m.id AND gh.competitor = 'h')
                                             JOIN core_matchstats ga 
                                               ON(ga.stat_type = 'xg' AND ga.period = {period} AND ga.match_id = m.id AND ga.competitor = 'a')
                                             JOIN betting_teamskill sh
                                               ON(sh.harvest_id = {harvest_pk} AND sh.team_id = m.team_h_id AND sh.param = 'h' AND 
                                                  sh.event_date < m.match_date AND sh.match_cnt > 3)
                                        WHERE  m.status = 'F'
                                          AND m.match_date BETWEEN %s AND %s
                                      ) d
                                    WHERE rn_h = 1
                                  ) d2
                                 JOIN betting_teamskill sa
                                   ON(sa.harvest_id = {harvest_pk} AND sa.team_id = d2.team_a_id AND sa.param = 'a' AND 
                                      sa.event_date < d2.match_date AND sa.match_cnt > 3)
                                WHERE rn_h = 1
                              ) d3
                            WHERE rn_a = 1
                              AND {team_str} >= %s AND {team_str} < %s
                              {value_filter}
                        ) d4
                      GROUP BY g_value
        """
        cursor.execute(sql_select, 
                              [self.start_date, self.end_date,
                               from_value, to_value,
                               ]
                             )
