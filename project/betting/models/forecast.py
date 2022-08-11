import traceback
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging

from django.db import models, transaction, connection
from django.utils import timezone
from django.db.models import sql, F, Q, Count, Max

from .betting import ValueType
from .probability import Distribution
from project.core.models import Sport, Match, League, Country, Team, LoadSource, Season
from project.load.models import ErrorLog
from project.betting.models import Odd
from .. import predictor_mixins as Mixins


logger = logging.getLogger(__name__)

################## Data prepartion ##################
class HarvestHandler(models.Model):

    slug = models.SlugField(unique=True)
    name = models.CharField('Harvest Type', max_length=100)
    param_descr = models.CharField('Parameter Description', max_length=1000, blank=True)
    handler = models.CharField('Handler', max_length=100, blank=True)

    def __str__(self):
        return self.name


class Harvest(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField('Script', max_length=100)
    comment = models.CharField('Comment', max_length=1000, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    harvest_handler = models.ForeignKey(HarvestHandler, on_delete=models.PROTECT, verbose_name='Harvest Type')
    value_type = models.ForeignKey(ValueType, on_delete=models.PROTECT, verbose_name='Vaue Type')
    period = models.IntegerField('Period')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')

    def __str__(self):
        return self.name

    @classmethod
    def api_do_harvest_all(cls, start_date=None):
        for harvest in Harvest.objects.filter(status=Harvest.ACTIVE).order_by("pk"):
            harvest.api_do_harvest(start_date)

    @classmethod
    def get_xg_harvest(cls, period=0, prefix="xg"):
        slug = prefix + "-" + str(period)
        harvest = Harvest.objects.filter(slug=slug).first()
        return harvest

    def do_harvest(self, start_date=None):
        from .harvest import TeamSkill
        for harvest_group in HarvestGroup.objects.filter(harvest=self).filter(status=Harvest.ACTIVE).order_by("pk"):
            harvest_group.do_harvest(start_date)

    def api_do_harvest(self, start_date=None):
        with transaction.atomic():
            self.do_harvest(start_date)


    def api_copy(self, slug, name):
        try:
            with transaction.atomic():
                harvest = Harvest.objects.create(
                                            slug=slug,
                                            name=name,
                                            comment=self.comment,
                                            sport=self.sport,
                                            harvest_handler=self.harvest_handler,
                                            value_type=self.value_type,
                                            period=self.period,
                                            status=self.INACTIVE
                                         )
                for harvest_config in HarvestConfig.objects.filter(harvest_id = self.id):
                    HarvestConfig.objects.create(harvest=harvest, code = harvest_config.code, value=harvest_config.value)
                for harvest_group in HarvestGroup.objects.filter(harvest_id = self.id):
                    harvest_group_slug = slug + harvest_group.slug[len(self.slug):]
                    new_harvest_group = HarvestGroup.objects.create(
                                            slug=harvest_group_slug,
                                            name=harvest_group.name,
                                            harvest=harvest,
                                            country=harvest_group.country,
                                            status=harvest_group.status,
                                            harvest_date=harvest_group.harvest_date,
                                            last_update=harvest_group.last_update
                                            )
                    for harvest_league in HarvestLeague.objects.filter(harvest_group_id=harvest_group.id):
                        HarvestLeague.objects.create(harvest_group=new_harvest_group, league=harvest_league.league)


        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Copy harvest Error"
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

    def adjust_params(self):
        from .harvest import TeamSkill
        print("Start adjusting")
        start_date = date(2015, 1, 1)

        # smooth-interval
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="smooth-interval")
        # start_interval = 10.0
        # step = 1.0
        # for x in range(10):
        #     smooth_interval = start_interval + x*step
        #     harvest_config.value = str(smooth_interval)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_xg_mse(self, start_date)
        #     print(smooth_interval, cnt, mse_h, mse_a)

        # # delta-koef
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="delta-koef-a")
        # start_interval = 3.6
        # step = 0.2
        # for x in range(10):
        #     delta_koef = start_interval + x*step
        #     harvest_config.value = str(delta_koef)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_xg_mse(self, start_date)
        #     print(round(delta_koef,1), cnt, mse_h, mse_a)


        # deviation-smooth-interval
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="deviation-smooth-interval")
        # start_interval = 15.0
        # step = 1.0
        # for x in range(10):
        #     smooth_interval = start_interval + x*step
        #     harvest_config.value = str(smooth_interval)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_g_mse(self, start_date)
        #     print(smooth_interval, cnt, mse_h, mse_a)

        # deviation-zero-value
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="deviation-zero-value")
        # start_interval = 0.24
        # step = 0.02
        # for x in range(10):
        #     zero_value = start_interval + x*step
        #     harvest_config.value = str(zero_value)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_g_mse(self, start_date)
        #     print(zero_value, cnt, mse_h, mse_a)

        # deviation-delta-koef
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="deviation-delta-koef-h")
        # start_interval = 4.6
        # step = 0.2
        # for x in range(10):
        #     zero_value = start_interval + x*step
        #     harvest_config.value = str(zero_value)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_g_mse(self, start_date)
        #     print(zero_value, cnt, mse_h, mse_a)


class HarvestConfig(models.Model):

    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    code = models.CharField('Code', max_length=100)
    value = models.CharField('Value', max_length=1000, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest','code'], name='unique_harvest_conf'),
        ]

    def __str__(self):
        return f'{self.harvest}:{self.code}:{self.value}'



class HarvestGroup(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField('Group', max_length=100)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')
    harvest_date = models.DateField('Harvest date', null=True, blank=True)
    last_update = models.DateTimeField('Last update', null=True, blank=True)

    def __str__(self):
        return self.name

    def do_harvest(self, start_date=None):
        from .harvest import TeamSkill

        if start_date:
            start_date = start_date - timedelta(days=10)
        else:
            if self.harvest_date:
                start_date = self.harvest_date - timedelta(days=10)
            else:
                start_date = date(2015, 1, 1)

        #delete old data
        TeamSkill.objects.filter(harvest_group=self, event_date__gte=start_date).delete()

        #harvesting
        harvest_config = {row.code:Decimal(row.value) for row in HarvestConfig.objects.filter(harvest = self.harvest)}
        harvest_date = None
        print("Harvest group", self, start_date)
        last_date = None
        cnt = 0
        for match in (Match.objects.filter(season__league__harvestleague__harvest_group = self, 
                                           match_date__gte = start_date,
                                           status=Match.FINISHED)
                                   .order_by("match_date","pk")
                     ):
            # print("Harvest match", match, match.match_date)
            cnt += 1
            last_date = match.match_date
            harvest_date = match.match_date
            TeamSkill.do_harvest(harvest=self.harvest, harvest_group = self, match=match, config=harvest_config)
        print("Cnt", cnt, "Last date", last_date)
        if harvest_date:
            self.harvest_date = harvest_date
            self.save()

    def api_do_harvest(self, start_date=None):
        with transaction.atomic():
            self.do_harvest(start_date)


class HarvestLeague(models.Model):

    harvest_group = models.ForeignKey(HarvestGroup, on_delete=models.CASCADE, verbose_name='Harvest Group')
    league = models.ForeignKey(League, on_delete=models.PROTECT, verbose_name='League')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['harvest_group','league'], name='unique_harvest_league'),
        ]

    def __str__(self):
        return f'{self.harvest_group}:{self.league}'




################## Forecast ##################
class ForecastHandler(models.Model):

    slug = models.SlugField(unique=True)
    name = models.CharField('Forecast Handler', max_length=100)
    handler = models.CharField('Handler', max_length=100, blank=True)

    def __str__(self):
        return self.name



class Predictor(models.Model):

    ACTIVE = 'a'
    INACTIVE = 'n'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    slug = models.SlugField(unique=True)
    name = models.CharField('Predictor', max_length=100)
    comment = models.CharField('Comment', max_length=1000, blank=True)
    forecast_handler = models.ForeignKey(ForecastHandler, on_delete=models.PROTECT, verbose_name='Forecast Type')
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    priority = models.IntegerField('Priority')
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='n')

    def __str__(self):
        return self.name

    ##################################################################################
    # methods to implement

    def extract_skills(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    def get_forecast_data(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    def get_distribution_slug(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " should implement this")

    def get_value_limit(self):
        min_value = None
        max_value = None

        if self.value_type_slug == "main":
            min_value = 0
            if self.period == 0:
                max_value = 7
            elif self.period in [1,2,]:
                max_value = 5
            else:
                max_value = 4
        return min_value, max_value

    ##################################################################################

    def get_real_predictor(self):
        real_cls = globals().get(self.forecast_handler.handler)
        if not real_cls:
            obj = self
        else:
            try:
                obj = real_cls.objects.get(pk=self.pk)
            except real_cls.DoesNotExist:
                obj = None
        return obj

    def get_distribution_data(self, slug, value, param="0", object_id=0):
        distribution_data = Distribution.get_distribution_data(slug, value, param, object_id)
        return distribution_data

    def forecasting(self, forecast_set, match_id=None, sandbox = False, period=None):
        from .harvest import TeamSkill
        start_date = forecast_set.start_date
        if not start_date:
            start_date = date(2015, 1, 1)

        status_field = "" if sandbox else "status, "
        table_dst = "betting_forecastsandbox" if sandbox else "betting_forecast"
        sql_insert_match_forecast = f"""
            INSERT INTO {table_dst}(
                forecast_set_id, match_id, odd_id, predictor_id, match_date, harvest_id,
                success_chance, lose_chance, result_value, kelly, {status_field} growth, odd_level, best_bet_type,
                best_odd)
            SELECT forecast_set_id, match_id, odd_id, predictor_id, match_date, harvest_id,
                   success_chance, lose_chance, result_value, kelly, {status_field} growth, odd_level, best_bet_type,
                   CASE WHEN best_bet_type = 0 THEN 0
                   ELSE ROW_NUMBER() OVER(PARTITION BY forecast_set_id, match_id, bookie_id
                                          ORDER BY CASE WHEN best_bet_type = 0 THEN 1 ELSE 0 END, odd_level, growth DESC, kelly DESC) 
                   END AS best_odd
                FROM 
                (
                SELECT t.*, o.bookie_id,
                       CASE WHEN t.odd_level = 0 THEN 0
                       ELSE ROW_NUMBER() OVER(PARTITION BY o.bookie_id, t.forecast_set_id, t.match_id, t.bet_type_slug, t.period, t.yes 
                                              ORDER BY CASE WHEN t.odd_level = 0 THEN 1 ELSE 0 END, t.growth DESC, t.kelly DESC) 
                       END AS best_bet_type
                  FROM betting_forecasttemp t, betting_odd o
                  WHERE t.forecast_set_id = %s AND t.match_id = %s
                    AND t.odd_id = o.id
                ) d
            """


        only_finished = forecast_set.only_finished
        keep_only_best = forecast_set.keep_only_best
        for harvest_league in HarvestLeague.objects.filter(harvest_group__harvest=self.harvest, harvest_group__status=HarvestGroup.ACTIVE):
            print(harvest_league)
            queryset = Match.objects.filter(league = harvest_league.league, 
                                            match_date__gte = start_date).select_related("league")
            if only_finished:
                queryset = queryset.exclude(status=Match.FINISHED)
            if match_id:
                queryset = queryset.filter(pk=match_id)
            queryset = queryset.order_by("match_date","pk")

            for match in queryset:
                print(match, match.match_date)

                if match.status == Match.FINISHED:
                    if Forecast.objects.filter(forecast_set_id=forecast_set.id,
                                               match_id=match.id,
                                               predictor_id=self.id,
                                               harvest_id=self.harvest.id, 
                                               ).exists():
                        if not Forecast.objects.filter(forecast_set_id=forecast_set.id,
                                                       match_id=match.id,
                                                       predictor_id=self.id,
                                                       harvest_id=self.harvest.id, 
                                                       status=Forecast.UNSETTLED
                                                   ).exists():
                            continue

                if not match.season or match.season.name == Season.UNKNOWN:
                    continue

                self.skill_h = {}
                self.skill_a = {}
                pattern = self.harvest.slug[:-1]
                qs = Harvest.objects.filter(slug__startswith=pattern, status=Harvest.ACTIVE)
                for hrvst in qs:

                    if sandbox:
                        self.skill_h[hrvst.period] = TeamSkillSandbox.objects.get(
                                                                    forecast_set_id=forecast_set.id,
                                                                    harvest_id=hrvst.id, 
                                                                    team_id=match.team_h_id, 
                                                                    event_date=match.match_date, 
                                                                    param="h")
                        self.skill_a[hrvst.period] = TeamSkillSandbox.objects.get(
                                                                    forecast_set_id=forecast_set.id,
                                                                    harvest_id=hrvst.id, 
                                                                    team_id=match.team_a_id, 
                                                                    event_date=match.match_date, 
                                                                    param="a")
                    else:    
                        self.skill_h[hrvst.period] = TeamSkill.get_team_skill(hrvst, match.team_h, match.match_date, match, param="h")
                        self.skill_a[hrvst.period] = TeamSkill.get_team_skill(hrvst, match.team_a, match.match_date, match, param="a")


                if not self.skill_h or not self.skill_a or self.skill_h[self.harvest.period].match_cnt <= 3 or self.skill_a[self.harvest.period].match_cnt <= 3:
                    continue



                #save forecast to temp table
                forecasts_tmp = []
                if sandbox:
                    qs_forecasts_tmp = ForecastSandbox.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id,).select_related("odd", "odd__bet_type")
                else:
                    qs_forecasts_tmp = Forecast.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id,).select_related("odd", "odd__bet_type")
                for f in qs_forecasts_tmp:
                    forecasts_tmp.append(ForecastTemp(forecast_set = f.forecast_set,
                                                      match = f.match,
                                                      odd = f.odd,
                                                      predictor = f.predictor,
                                                      match_date = f.match_date,
                                                      harvest = f.harvest,
                                                      success_chance = f.success_chance,
                                                      lose_chance = f.lose_chance,
                                                      result_value = f.result_value,
                                                      kelly = f.kelly,
                                                      status = "u" if sandbox else f.status,
                                                      growth = f.growth,
                                                      odd_level = f.odd_level,
                                                      bet_type_slug = f.odd.bet_type.slug,
                                                      period = f.odd.period,
                                                      yes = f.odd.yes,
                                                      team = f.odd.team,
                                                      param = f.odd.param,
                                                      odd_value = f.odd.odd_value,
                                                     )
                                        )
                ForecastTemp.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id,).delete()
                ForecastTemp.objects.bulk_create(forecasts_tmp)


                queryset = Harvest.objects.filter(slug__startswith=pattern, status=Harvest.ACTIVE)
                if period != None:
                    queryset = queryset.filter(period=period)
                for harvest in queryset:

                    self.period = harvest.period
                    self.value_type_slug = harvest.value_type.slug
                    self.value_type = harvest.value_type

                    self.extract_skills()
                    forecast_data = self.get_forecast_data(object_id=harvest_league.league.id)


                    # print("dl", sum([d[2] for d in forecast_data if d[0] <= d[1]]))
                    # print("wl", sum([d[2] for d in forecast_data if d[0] != d[1]]))
                    forecast_ins = []
                    forecast_upd = []
                    i = 0
                    for odd in Odd.objects.filter(match=match, value_type=self.value_type, period=self.period).select_related("bet_type"):
                        i += 1
                        forecast_old = None
                        ins = False
                        upd = False
                        if sandbox:
                            forecast_old = ForecastTemp.objects.filter(forecast_set_id=forecast_set.id,
                                                                          match_id=match.id,
                                                                          odd_id=odd.id,
                                                                          predictor_id=self.id).first()
                            if forecast_old:
                                continue
                            ins = True
                        else:
                            forecast_old = ForecastTemp.objects.filter(forecast_set_id=forecast_set.id,
                                                                   match_id=match.id,
                                                                   odd_id=odd.id,
                                                                   predictor_id=self.id).first()
                            if forecast_old:
                                upd = True
                                # print("forecast_old.status",forecast_old.status)
                                if forecast_old.status == Forecast.SETTLED:
                                    continue
                            else:
                                ins = True

                        real_odd = odd.get_own_object()
                        success_chance, lose_chance, result_value = real_odd.forecasting(forecast_data)
                        if success_chance != None:
                            kelly = 0
                            growth = 0
                            if result_value > 1.001:
                                kelly = (result_value - Decimal(1.0)) / (odd.odd_value - Decimal(1.0))
                                growth = Decimal(1.0) - kelly + kelly*result_value
                            if ins:
                                forecast_temp = ForecastTemp(
                                                                forecast_set = forecast_set,
                                                                match = match,
                                                                odd = odd,
                                                                predictor = self,
                                                                match_date = match.match_date,
                                                                harvest = harvest,
                                                                success_chance = success_chance,
                                                                lose_chance = lose_chance,
                                                                result_value = result_value,
                                                                kelly = kelly,
                                                                status = Forecast.SETTLED if odd.status==Odd.FINISHED else Forecast.UNSETTLED,
                                                                growth = growth,
                                                                odd_level = 0,
                                                                bet_type_slug = odd.bet_type.slug,
                                                                period = odd.period,
                                                                yes = odd.yes,
                                                                team = odd.team,
                                                                param = odd.param,
                                                                odd_value = odd.odd_value,
                                                            )
                                forecast_temp.set_odd_level()
                                forecast_ins.append(forecast_temp)
                            elif upd:
                                forecast_old.success_chance=success_chance
                                forecast_old.lose_chance=lose_chance
                                forecast_old.result_value=result_value
                                forecast_old.kelly=kelly
                                forecast_old.status=Forecast.SETTLED if odd.status==Odd.FINISHED else Forecast.UNSETTLED
                                forecast_old.growth=growth
                                forecast_old.odd_level=0
                                forecast_old.set_odd_level()
                                forecast_upd.append(forecast_old)


                    if forecast_ins:
                        ForecastTemp.objects.bulk_create(forecast_ins)
                    if forecast_upd:
                        ForecastTemp.objects.bulk_update(forecast_upd, ["success_chance","lose_chance","result_value","kelly","status","growth","odd_level"])

                # Save prepared match forecasting to table
                if sandbox:
                    ForecastSandbox.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id).delete()
                else:
                    Forecast.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id).delete()
                with connection.cursor() as cursor:
                    cursor.execute(sql_insert_match_forecast, [forecast_set.id, match.id, ])
                ForecastTemp.objects.filter(forecast_set_id=forecast_set.id, match_id=match.id).delete()

                

    def forecasting_odd(self, odd):
        from .harvest import TeamSkill
        predictor = self.get_real_predictor()

        predictor.period = odd.period
        predictor.value_type_slug = odd.value_type.slug
        predictor.value_type = odd.value_type

        pattern = predictor.harvest.slug[:-1]
        predictor.skill_h = {}
        predictor.skill_a = {}
        qs = Harvest.objects.filter(slug__startswith=pattern, status=Harvest.ACTIVE)
        for hrvst in qs:
            predictor.skill_h[hrvst.period] = TeamSkill.get_team_skill(
                                                        hrvst, 
                                                        odd.match.team_h, 
                                                        odd.match.match_date, 
                                                        odd.match, 
                                                        param="h")
            predictor.skill_a[hrvst.period] = TeamSkill.get_team_skill(
                                                        hrvst, 
                                                        odd.match.team_a, 
                                                        odd.match.match_date, 
                                                        odd.match, 
                                                        param="a")
        predictor.extract_skills()
        forecast_data = predictor.get_forecast_data()
        real_odd = odd.get_own_object()
        real_odd.odd_value = odd.odd_value
        success_chance, lose_chance, result_value = real_odd.forecasting(forecast_data)
        kelly = 0
        if result_value > 1.001:
            kelly = (result_value - Decimal(1.0)) / (Decimal(odd.odd_value) - Decimal(1.0))
        return success_chance, lose_chance, result_value, kelly


class ForecastSet(models.Model):

    PREPARED = 'p'
    SUCCESS = 's'
    ERROR = 'e'

    STATUS_CHOICES = (
        (PREPARED, 'Prepared'),
        (SUCCESS, 'Success'),
        (ERROR, 'Error'),
    )


    slug = models.SlugField(unique=True)
    name = models.CharField('Name', max_length=255, blank=True)
    forecast_date = models.DateTimeField('Forecast date', null=True, blank=True)
    forecast_time = models.IntegerField('Seconds', null=True)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='p')
    match_cnt = models.IntegerField('Matches', null=True)
    odd_cnt = models.IntegerField('Odds', null=True)
    keep_only_best = models.BooleanField('Keep only best prediction')
    only_finished = models.BooleanField('Only finished matches')
    start_date = models.DateField('Start date', null=True, blank=True)

    def __str__(self):
        return self.slug

    @classmethod
    def api_create(cls, slug, name, start_date):
        try:
            with transaction.atomic():
                forecast_set = ForecastSet.objects.create(
                                    slug = slug,
                                    name = name,
                                    forecast_date = datetime.now(),
                                    status = ForecastSet.PREPARED,
                                    match_cnt = 0,
                                    odd_cnt = 0,
                                    keep_only_best = False,
                                    only_finished = False,
                                    start_date = start_date
                                    )
                forecast_set.forecasting()
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


    def api_update(self, slug, name, delete_old, start_date):
        try:
            with transaction.atomic():
                self.slug = slug
                self.name = name
                self.forecast_date = datetime.now()
                self.status = ForecastSet.PREPARED
                self.match_cnt = 0
                self.odd_cnt = 0
                self.keep_only_best = False
                self.only_finished = False
                self.start_date = start_date
                self.save()
                self.forecasting(delete_old=delete_old)
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


    def api_update_match_xG(self, harvest, match, xG_h, xA_h, G_h, A_h, xG_a, xA_a, G_a, A_a, period=0):
        from .harvest import TeamSkill
        try:
            with transaction.atomic():
                tsh = TeamSkill.get_team_skill(harvest=harvest, team=match.team_h, skill_date=match.match_date, param="h")
                tsa = TeamSkill.get_team_skill(harvest=harvest, team=match.team_a, skill_date=match.match_date, param="a")
                xG_h0 = (TeamSkillSandbox.objects
                                .filter(forecast_set=self, harvest=harvest, team=match.team_h, event_date=match.match_date, param="h")
                                .update(value1 =xG_h,
                                        value2 =xA_h,
                                        value9 =G_h,
                                        value10=A_h,
                                        changed1 = (not (xG_h==round(tsh.value1,3))),
                                        changed2 = (not (xA_h==round(tsh.value2,3))),
                                        changed9 = (not (G_h==round(tsh.value9,3))),
                                        changed10= (not (A_h==round(tsh.value10,3))),
                                       )
                         )
                xG_a0 = (TeamSkillSandbox.objects
                                .filter(forecast_set=self, harvest=harvest, team=match.team_a, event_date=match.match_date, param="a")
                                .update(value1 =xG_a,
                                        value2 =xA_a,
                                        value9 =G_a,
                                        value10=A_a,
                                        changed1 = (not (xG_a==round(tsa.value1,3))),
                                        changed2 = (not (xA_a==round(tsa.value2,3))),
                                        changed9 = (not (G_a==round(tsa.value9,3))),
                                        changed10= (not (A_a==round(tsa.value10,3))),
                                       )
                         )
                self.forecast_match(match, period=period)

        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Updating xG Error"
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


    def api_restore_match_xG(self, harvest, match):
        try:
            with transaction.atomic():
                self.restore_forecast(match, harvest)

        except Exception as e:
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Restoring xG Error"
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



    def _add_teamskill_sandbox(self, harvest, team, event_date, param):
        from .harvest import TeamSkill
        exist_skill = TeamSkillSandbox.objects.filter(forecast_set=self, harvest=harvest, team=team, param=param, event_date=event_date).exists()
        if not exist_skill:
            ts = TeamSkill.get_team_skill(harvest=harvest, team=team, skill_date=event_date, param=param)
            if ts:
                TeamSkillSandbox.objects.create(forecast_set = self,
                                                harvest = ts.harvest,
                                                harvest_group = ts.harvest_group,
                                                team = ts.team,
                                                event_date = event_date,
                                                match = ts.match,
                                                match_cnt = ts.match_cnt,
                                                lvalue1  = ts.lvalue1,
                                                lvalue2  = ts.lvalue2,
                                                lvalue3  = ts.lvalue3,
                                                lvalue4  = ts.lvalue4,
                                                lvalue5  = ts.lvalue5,
                                                lvalue6  = ts.lvalue6,
                                                lvalue7  = ts.lvalue7,
                                                lvalue8  = ts.lvalue8,
                                                lvalue9  = ts.lvalue9,
                                                lvalue10 = ts.lvalue10,
                                                value1   = ts.value1,
                                                value2   = ts.value2,
                                                value3   = ts.value3,
                                                value4   = ts.value4,
                                                value5   = ts.value5,
                                                value6   = ts.value6,
                                                value7   = ts.value7,
                                                value8   = ts.value8,
                                                value9   = ts.value9,
                                                value10  = ts.value10,
                                                param    = ts.param
                                                )


    def prepare_sandbox(self, match, harvest):
        self._add_teamskill_sandbox(harvest=harvest, team=match.team_h, event_date=match.match_date, param='h')
        self._add_teamskill_sandbox(harvest=harvest, team=match.team_a, event_date=match.match_date, param='a')
        if not ForecastSandbox.objects.filter(forecast_set=self, match=match).exists():
            forecasts = [ForecastSandbox(   forecast_set_id = self.id,
                                            match_id = f.match_id,
                                            odd_id = f.odd_id,
                                            predictor_id = f.predictor_id,
                                            match_date = f.match_date,
                                            harvest_id = f.harvest_id,
                                            success_chance  = f.success_chance,
                                            lose_chance  = f.lose_chance,
                                            result_value = f.result_value,
                                            kelly = f.kelly,
                                            growth = f.growth,
                                            odd_level = f.odd_level, 
                                            best_bet_type = f.best_bet_type, 
                                            best_odd = f.best_odd 
                                        ) for f in Forecast.objects.filter(forecast_set_id=self.id, match_id=match.id)]
            ForecastSandbox.objects.bulk_create(forecasts)
            


    def restore_forecast(self, match, harvest):
        TeamSkillSandbox.objects.filter(forecast_set=self, 
                                        team=match.team_h, 
                                        event_date=match.match_date, 
                                        param='h').delete()
        TeamSkillSandbox.objects.filter(forecast_set=self, 
                                        team=match.team_a, 
                                        event_date=match.match_date, 
                                        param='a').delete()
        ForecastSandbox.objects.filter(forecast_set=self, match=match).delete()
        self.prepare_sandbox(match, harvest)


    def forecasting(self, delete_old=False):
        start_time = datetime.now()

        for m in ForecastSandbox.objects.filter(forecast_set=self).order_by("match_id").distinct("match_id"): 
            mid = m.match_id
            if not TeamSkillSandbox.objects.filter(Q(forecast_set=self) & Q(match_id=mid) &
                                                   (Q(changed1=True) | Q(changed2=True) | Q(changed3=True) | Q(changed4=True) | Q(changed5=True) |
                                                    Q(changed6=True) | Q(changed7=True) | Q(changed8=True) | Q(changed9=True) | Q(changed10=True) 
                                                    )
                                                  ):
                ForecastSandbox.objects.filter(forecast_set=self, match_id=m.match_id).delete()
                TeamSkillSandbox.objects.filter(forecast_set=self, match_id=m.match_id).delete()
        if delete_old:
            Forecast.objects.filter(forecast_set=self).delete()
        for predictor in Predictor.objects.filter(status=Predictor.ACTIVE).order_by("priority", "pk"):
            print("<<<predictor>>>", predictor)
            real_predictor = predictor.get_real_predictor()
            real_predictor.forecasting(self)
        print("<<<finish>>>")

        odd_cnt = Forecast.objects.filter(forecast_set=self).count()
        match_cnt = Forecast.objects.filter(forecast_set=self).distinct('match').count()
        finish_time = datetime.now()
        duration = finish_time - start_time
        self.forecast_date = start_time
        self.forecast_time = duration.total_seconds()
        self.match_cnt = match_cnt
        self.odd_cnt = odd_cnt
        self.status = ForecastSet.SUCCESS
        self.save()

    def forecast_match(self, match, period=None):
        ForecastSandbox.objects.filter(forecast_set=self, match=match).delete()
        for predictor in Predictor.objects.filter(status=Predictor.ACTIVE).order_by("priority", "pk"):
            real_predictor = predictor.get_real_predictor()
            real_predictor.forecasting(self, match_id=match.id, sandbox=True, period=period)



class Forecast(models.Model):
    #Status
    SETTLED  = 's'
    UNSETTLED = 'u'

    STATUS_CHOICES = (
        (SETTLED, 'Settled'),
        (UNSETTLED, 'Unsettled'),
    )


    forecast_set = models.ForeignKey(ForecastSet, on_delete=models.CASCADE, verbose_name='Forecast set')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE, verbose_name='Odd')
    predictor = models.ForeignKey(Predictor, on_delete=models.CASCADE, verbose_name='Predictor')
    match_date = models.DateField('Match date', null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    kelly = models.DecimalField('kelly', max_digits=10, decimal_places=3)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='u')

    growth = models.DecimalField('growth', max_digits=10, decimal_places=6, null=True)
    odd_level = models.IntegerField('Odd Level', null=True) 
    best_bet_type = models.IntegerField('Best Bet Type', null=True) 
    best_odd = models.IntegerField('Best Odd', null=True) 

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["forecast_set", "match", "odd", "predictor" ], name='unique_forecast'),
        ]

    def __str__(self):
        return f'Set:{self.forecast_set},M:<{self.match},{self.match_date}>,Odd:<{self.odd}>,P:{self.predictor},R:{round(self.result_value,4)},S:{round(self.success_chance,4)}'


class ForecastSandbox(models.Model):

    forecast_set = models.ForeignKey(ForecastSet, on_delete=models.CASCADE, verbose_name='Forecast set')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE, verbose_name='Odd')
    predictor = models.ForeignKey(Predictor, on_delete=models.CASCADE, verbose_name='Predictor')
    match_date = models.DateField('Match date', null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    kelly = models.DecimalField('kelly', max_digits=10, decimal_places=3)

    growth = models.DecimalField('growth', max_digits=10, decimal_places=6, null=True)
    odd_level = models.IntegerField('Odd Level', null=True) 
    best_bet_type = models.IntegerField('Best Bet Type', null=True) 
    best_odd = models.IntegerField('Best Odd', null=True) 

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["forecast_set", "match", "odd", "predictor" ], name='unique_forecast_sandbox'),
        ]

    def __str__(self):
        return f'Set:{self.forecast_set},M:<{self.match},{self.match_date}>,Odd:<{self.odd}>,P:{self.predictor},R:{round(self.result_value,4)},S:{round(self.success_chance,4)}'


class ForecastTemp(models.Model):

    forecast_set = models.ForeignKey(ForecastSet, on_delete=models.CASCADE, verbose_name='Forecast set')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE, verbose_name='Odd')
    predictor = models.ForeignKey(Predictor, on_delete=models.CASCADE, verbose_name='Predictor')
    match_date = models.DateField('Match date', null=True, blank=True)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE, verbose_name='Harvest')
    success_chance  = models.DecimalField('Success chance', max_digits=10, decimal_places=3)
    lose_chance  = models.DecimalField('Lose chance', max_digits=10, decimal_places=3)
    result_value = models.DecimalField('Result value', max_digits=10, decimal_places=3)
    kelly = models.DecimalField('kelly', max_digits=10, decimal_places=3)
    status = models.CharField('Status', max_length=5, default='u')

    growth = models.DecimalField('growth', max_digits=10, decimal_places=6, null=True)
    odd_level = models.IntegerField('Odd Level', null=True) 

    bet_type_slug = models.CharField('Bet_Type Slug', max_length=100)
    period = models.IntegerField('Period')
    yes = models.CharField(r'Yes\No', max_length=1)
    team = models.CharField('Team', max_length=10, blank=True)
    param = models.CharField('Param', max_length=255, blank=True)
    odd_value = models.DecimalField('Odd', max_digits=10, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["forecast_set", "match", "odd", "predictor" ], name='unique_forecasttest'),
        ]

    def __str__(self):
        return f'Set:{self.forecast_set},M:<{self.match},{self.match_date}>,Odd:<{self.bet_type_slug},{self.period},{self.team},{self.param},{self.odd_value}>'

    def set_odd_level(self):
        if self.growth <= 0:
            return
        if self.match.league.slug == "english-premier-league":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "Y" and 
                    self.odd_value >= Decimal(2.2) and self.odd_value <= Decimal(6.6)
                    ):
                    # 1 success=0.37 avg_profit=0.33
                    self.odd_level = 1
                elif (  self.bet_type_slug == "handicap" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(3.6)
                        ):
                    # 2 success=0.38 avg_profit=0.0947
                    self.odd_level = 2
                elif (  self.bet_type_slug == "wdl" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(3.5)
                        ):
                    # 3 success=0.425 avg_profit=0.11
                    self.odd_level = 3
                elif (  self.bet_type_slug == "itotal_both_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(1.7)
                        ):
                    # 2 success=0.75 avg_profit=0.2
                    self.odd_level = 2
                elif (  self.bet_type_slug == "margin" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(2.1)
                        ):
                    # 3 success=0.7 avg_profit=0.16
                    self.odd_level = 3
                elif (  self.bet_type_slug == "total_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.5) and self.odd_value <= Decimal(6.4)
                        ):
                    # 2 success=0.35 avg_profit=0.13
                    self.odd_level = 2
                elif (  self.bet_type_slug == "w_and_total" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.3) and self.odd_value <= Decimal(4.5)
                        ):
                    # 3 success=0.33 avg_profit=0.21
                    self.odd_level = 3
                elif (  self.bet_type_slug == "w_and_total_over" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.3) and self.odd_value <= Decimal(4.2)
                        ):
                    # 2 success=0.36 avg_profit=0.132
                    self.odd_level = 2
                elif (  self.bet_type_slug == "wd_and_total_over" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.7) and self.odd_value <= Decimal(2.0)
                        ):
                    # 2 success=0.70 avg_profit=0.31
                    self.odd_level = 2

        elif self.match.league.slug == "french-ligue-1":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "Y" and 
                    self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(4.3)
                    ):
                    # 2 success=0.38 avg_profit=0.12
                    self.odd_level = 2
                elif (  self.bet_type_slug == "handicap" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.7) and self.odd_value <= Decimal(2.0)
                        ):
                    # 1 success=0.56 avg_profit=0.09
                    self.odd_level = 1
            elif self.predictor.slug == "xg-orig-fix":
                if (self.bet_type_slug == "w_and_itotal_under" and self.period == 0 and self.yes == "Y" and 
                    self.odd_value >= Decimal(3.2) and self.odd_value <= Decimal(8.5)
                    ):
                    # 3 success=0.244 avg_profit=0.35
                    self.odd_level = 3

        elif self.match.league.slug == "german-bundesliga":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "both_to_score_at_1_2" and self.period == 0 and self.yes == "Y" and 
                    self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(5.6)
                    ):
                    # 2 success=0.352 avg_profit=0.541
                    self.odd_level = 2
                elif (  self.bet_type_slug == "itotal_both_over" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.0) and self.odd_value <= Decimal(5.3)
                        ):
                    # 2 success=0.35 avg_profit=0.47
                    self.odd_level = 2
                elif (  self.bet_type_slug == "handicap" and self.period in(0,1,) and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.9) and self.odd_value <= Decimal(7.0)
                        ):
                    # 3 success=0.37 avg_profit=0.098
                    self.odd_level = 3
                elif (  self.bet_type_slug == "wdl" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.3) and self.odd_value <= Decimal(6.6)
                        ):
                    # 1 success=0.34 avg_profit=0.20
                    self.odd_level = 1
                elif (  self.bet_type_slug == "total_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.0) and self.odd_value <= Decimal(7.0)
                        ):
                    # 3 success=0.41 avg_profit=0.065
                    self.odd_level = 3
                elif (  self.bet_type_slug == "w_and_itotal_over" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.9) and self.odd_value <= Decimal(7.0)
                        ):
                    # 2 success=0.46 avg_profit=0.17
                    self.odd_level = 2
                elif (  self.bet_type_slug == "w_and_total_under" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(6.0)
                        ):
                    # 2 success=0.45 avg_profit=0.10
                    self.odd_level = 2
                elif (  self.bet_type_slug == "wd_and_itotal_over" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(6.0)
                        ):
                    # 1 success=0.45 avg_profit=0.31
                    self.odd_level = 1
                elif (  self.bet_type_slug == "wd_and_total_under" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(2.3) and self.odd_value <= Decimal(4.3)
                        ):
                    # 3 success=0.37 avg_profit=0.0533
                    self.odd_level = 3

        elif self.match.league.slug == "italian-serie-a":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "N" and 
                    self.odd_value >= Decimal(1.7) and self.odd_value <= Decimal(4.1)
                    ):
                    # 2 success=0.5 avg_profit=0.374
                    self.odd_level = 2
                elif (  self.bet_type_slug == "itotal_both_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(5.0)
                        ):
                    # 1 success=0.46 avg_profit=0.35
                    self.odd_level = 1
                elif (  self.bet_type_slug == "total" and self.period == 0 and self.yes == "Y" and 
                        self.param != "2,3" and
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(3.9)
                        ):
                    # 1 success=0.53 avg_profit=0.246
                    self.odd_level = 1
                elif (  self.bet_type_slug == "total" and self.period in(1,2,) and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(3.9)
                        ):
                    # 1 success=0.53 avg_profit=0.59
                    self.odd_level = 1
                elif (  self.bet_type_slug == "handicap" and self.period == 0 and self.yes == "Y" and 
                        self.team == "a" and
                        self.odd_value >= Decimal(1.6) and self.odd_value <= Decimal(2.9)
                        ):
                    # 1 success=0.60 avg_profit=0.193
                    self.odd_level = 1
                elif (  self.bet_type_slug == "wdl" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(1.7)
                        ):
                    # 3 success=0.76 avg_profit=0.178
                    self.odd_level = 3
                elif (  self.bet_type_slug == "wdl" and self.period == 1 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(6.0)
                        ):
                    # 1 success=0.48 avg_profit=0.365
                    self.odd_level = 1
                elif (  self.bet_type_slug == "total_both_halves_under" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.8) and self.odd_value <= Decimal(3.7)
                        ):
                    # 2 success=0.48 avg_profit=0.12
                    self.odd_level = 2
                elif (  self.bet_type_slug == "total_over" and self.period == 2 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.1) and self.odd_value <= Decimal(3.0)
                        ):
                    # 3 success=0.4 avg_profit=0.13
                    self.odd_level = 3
                elif (  self.bet_type_slug == "total_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.7) and self.odd_value <= Decimal(3.3)
                        ):
                    # 1 success=0.63 avg_profit=0.25
                    self.odd_level = 1
                elif (  self.bet_type_slug == "w_and_itotal_over" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(3.5)
                        ):
                    # 1 success=0.6 avg_profit=0.182
                    self.odd_level = 1
                elif (  self.bet_type_slug == "w_and_total_over" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.3) and self.odd_value <= Decimal(3.9)
                        ):
                    # 1 success=0.69 avg_profit=0.15
                    self.odd_level = 1
                elif (  self.bet_type_slug == "wd_and_total_over" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(2.1)
                        ):
                    # 2 success=0.66 avg_profit=0.176
                    self.odd_level = 2
                elif (  self.bet_type_slug == "wd_and_total_under" and self.period == 0 and self.yes == "Y" and 
                        self.param == "3.5" and
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(2.2)
                        ):
                    # 3 success=0.71 avg_profit=0.264
                    self.odd_level = 3

        elif self.match.league.slug == "russian-premier-league":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "N" and 
                    self.odd_value >= Decimal(2.4) and self.odd_value <= Decimal(3.6)
                    ):
                    # 2 success=0.5 avg_profit=0.336
                    self.odd_level = 2
                elif (  self.bet_type_slug == "total" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(2.3)
                        ):
                    # 1 success=0.72 avg_profit=0.3
                    self.odd_level = 1
                elif (  self.bet_type_slug == "handicap" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.6) and self.odd_value <= Decimal(4.1)
                        ):
                    # 3 success=0.467 avg_profit=0.073
                    self.odd_level = 3
                elif (  self.bet_type_slug == "wdl" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(4.4)
                        ):
                    # 2 success=0.44 avg_profit=0.18
                    self.odd_level = 2
                elif (  self.bet_type_slug == "total_over" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(3.4)
                        ):
                    # 2 success=0.56 avg_profit=0.14
                    self.odd_level = 2
                elif (  self.bet_type_slug == "wdl_and_both_teams_score" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.9) and self.odd_value <= Decimal(5.6)
                        ):
                    # 3 success=0.5 avg_profit=0.828
                    self.odd_level = 3
                elif (  self.bet_type_slug == "w_and_total_under" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.4) and self.odd_value <= Decimal(2.7)
                        ):
                    # 3 success=0.627 avg_profit=0.13
                    self.odd_level = 3
                elif (  self.bet_type_slug == "w_and_total_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(2.8)
                        ):
                    # 3 success=0.53 avg_profit=0.19
                    self.odd_level = 3
                elif (  self.bet_type_slug == "wd_and_total_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(2.0) and self.odd_value <= Decimal(6.6)
                        ):
                    # 3 success=0.4 avg_profit=0.113
                    self.odd_level = 3
                elif (  self.bet_type_slug == "win_to_nil" and self.period == 0 and self.yes == "N" and 
                        self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(3.5)
                        ):
                    # 2 success=0.76 avg_profit=0.29
                    self.odd_level = 2

        elif self.match.league.slug == "spanish-primera-division":
            if self.predictor.slug == "xg-std-fix":
                if (self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "N" and 
                    self.odd_value >= Decimal(1.8) and self.odd_value <= Decimal(3.1)
                    ):
                    # 2 success=0.54 avg_profit=0.19
                    self.odd_level = 2
                elif (  self.bet_type_slug == "itotal_at_least_over" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.6) and self.odd_value <= Decimal(3.1)
                        ):
                    # 3 success=0.61 avg_profit=0.175
                    self.odd_level = 3
                elif (  self.bet_type_slug == "itotal_both_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.6) and self.odd_value <= Decimal(6.3)
                        ):
                    # 1 success=0.51 avg_profit=0.21
                    self.odd_level = 1
                elif (  self.bet_type_slug == "total_both_halves_under" and self.period == 0 and self.yes == "Y" and 
                        self.odd_value >= Decimal(1.7) and self.odd_value <= Decimal(3.9)
                        ):
                    # 2 success=0.5 avg_profit=0.31
                    self.odd_level = 2
            if self.predictor.slug == "xg-orig-fix":
                if (self.bet_type_slug == "total" and self.period == 0 and self.yes == "N" and 
                    self.param != "0,1" and
                    self.odd_value >= Decimal(1.5) and self.odd_value <= Decimal(2.9)
                    ):
                    # 3 success=0.7 avg_profit=0.245
                    self.odd_level = 3
                elif (  self.bet_type_slug == "total_over" and self.period == 2 and self.yes == "Y" and 
                        self.param == "0.50" and
                        self.odd_value >= Decimal(1.6) and self.odd_value <= Decimal(2.9)
                        ):
                    # 3 success=0.545 avg_profit=0.236
                    self.odd_level = 3


class TeamSkillSandbox(models.Model):

    forecast_set = models.ForeignKey(ForecastSet, on_delete=models.CASCADE, verbose_name='Forecast set')
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

    changed1 = models.BooleanField(default=False)
    changed2 = models.BooleanField(default=False)
    changed3 = models.BooleanField(default=False)
    changed4 = models.BooleanField(default=False)
    changed5 = models.BooleanField(default=False)
    changed6 = models.BooleanField(default=False)
    changed7 = models.BooleanField(default=False)
    changed8 = models.BooleanField(default=False)
    changed9 = models.BooleanField(default=False)
    changed10 = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['forecast_set','harvest','team','param','event_date','match'], name='unique_teamskill_sandbox'),
        ]
        indexes = [
            models.Index(fields=['forecast_set','harvest_group','event_date'], name='tskill_snd_hgrp_edate_idx'),
        ]

    def __str__(self):
        return f'W:{self.harvest},T:{self.team},D:{self.event_date}'



###################################################################
class PredictorStandardPoisson(Mixins.StandartExtraction, Mixins.PoissonForecasting, Predictor):
    class Meta:
        proxy = True

class PredictorDistributionXG(Mixins.OriginalDataExtraction, Mixins.FixedDistributionForecasting, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-distr"

class PredictorStdDistribH_XG_0(Mixins.StandartExtraction, Mixins.FixedDistributionForecasting, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-ext-distr"

class PredictorOrigDistrXG(Mixins.OriginalDataExtraction, Mixins.FixedDistributionForecasting, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-distr-copy"

class PredictorStdDistrXG(Mixins.StandartExtraction, Mixins.FixedDistributionForecasting, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-ext-distr-copy"
