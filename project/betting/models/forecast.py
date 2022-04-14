import traceback
from decimal import Decimal
from datetime import datetime, date, timedelta
import logging

from django.db import models, transaction
from django.utils import timezone
from django.db.models import sql, F, Q, Count, Max

from .betting import ValueType
from .probability import Distribution
from project.core.models import Sport, Match, League, Country, Team, LoadSource
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
        # start_interval = 7.0
        # step = 1.0
        # for x in range(10):
        #     smooth_interval = start_interval + x*step
        #     harvest_config.value = str(smooth_interval)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_xg_mse(self, start_date)
        #     print(smooth_interval, cnt, mse_h, mse_a)

        # delta-koef
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="delta-koef-h")
        # start_interval = 2.6
        # step = 0.2
        # for x in range(10):
        #     delta_koef = start_interval + x*step
        #     harvest_config.value = str(delta_koef)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_xg_mse(self, start_date)
        #     print(delta_koef, cnt, mse_h, mse_a)


        # deviation-smooth-interval
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="deviation-smooth-interval")
        # start_interval = 6.0
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
        # start_interval = 0.55
        # step = 0.05
        # for x in range(10):
        #     zero_value = start_interval + x*step
        #     harvest_config.value = str(zero_value)
        #     harvest_config.save()
        #     self.do_harvest(date(2014, 8, 1))
        #     cnt, mse_h, mse_a = TeamSkill.calculate_g_mse(self, start_date)
        #     print(zero_value, cnt, mse_h, mse_a)

        # deviation-delta-koef
        # harvest_config = HarvestConfig.objects.get(harvest=self, code="deviation-delta-koef-a")
        # start_interval = 2.6
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

    def forecasting(self, forecast_set, match_id=None, sandbox = False):
        from .harvest import TeamSkill
        start_date = forecast_set.start_date
        if not start_date:
            start_date = date(2015, 1, 1)

        self.period = self.harvest.period
        self.value_type_slug = self.harvest.value_type.slug
        self.value_type = self.harvest.value_type

        only_finished = forecast_set.only_finished
        keep_only_best = forecast_set.keep_only_best
        print(3, self.harvest)
        for harvest_league in HarvestLeague.objects.filter(harvest_group__harvest=self.harvest, harvest_group__status=HarvestGroup.ACTIVE):
            print(harvest_league)
            queryset = Match.objects.filter(season__league = harvest_league.league, 
                                            match_date__gte = start_date)
            if only_finished:
                queryset = queryset.exclude(status=Match.FINISHED)
            if match_id:
                queryset = queryset.filter(pk=match_id)
            queryset = queryset.order_by("match_date","pk")

            for match in queryset:
                print(match, match.match_date)
                if sandbox:
                    self.skill_h = TeamSkillSandbox.objects.get(forecast_set_id=forecast_set.id,
                                                                harvest_id=self.harvest_id, 
                                                                team_id=match.team_h_id, 
                                                                event_date=match.match_date, 
                                                                param="h")
                    self.skill_a = TeamSkillSandbox.objects.get(forecast_set_id=forecast_set.id,
                                                                harvest_id=self.harvest_id, 
                                                                team_id=match.team_a_id, 
                                                                event_date=match.match_date, 
                                                                param="a")
                else:    
                    if match.status == Match.FINISHED:
                        if Forecast.objects.filter(forecast_set_id=forecast_set.id,
                                                   match_id=match.id,
                                                   predictor_id=self.id,
                                                   ).exists():
                            if not Forecast.objects.filter(forecast_set_id=forecast_set.id,
                                                           match_id=match.id,
                                                           predictor_id=self.id,
                                                           status=Forecast.UNSETTLED
                                                       ).exists():
                                continue
                    self.skill_h = TeamSkill.get_team_skill(self.harvest, match.team_h, match.match_date, match, param="h")
                    self.skill_a = TeamSkill.get_team_skill(self.harvest, match.team_a, match.match_date, match, param="a")


                if not self.skill_h or not self.skill_a or self.skill_h.match_cnt <= 3 or self.skill_a.match_cnt <= 3:
                    continue

                self.extract_skills()
                forecast_data = self.get_forecast_data()

                # print("dl", sum([d[2] for d in forecast_data if d[0] <= d[1]]))
                # print("wl", sum([d[2] for d in forecast_data if d[0] != d[1]]))
                forecast_ins = []
                forecast_upd = []
                for odd in Odd.objects.filter(match=match, value_type=self.value_type, period=self.period):
                    forecast_old = None
                    ins = False
                    upd = False
                    if sandbox:
                        forecast_old = ForecastSandbox.objects.filter(forecast_set_id=forecast_set.id,
                                                                      match_id=match.id,
                                                                      odd_id=odd.id,
                                                                      predictor_id=self.id).first()
                        if forecast_old:
                            continue
                        ins = True
                    else:
                        forecast_old = Forecast.objects.filter(forecast_set_id=forecast_set.id,
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
                        if result_value > 1.001:
                            kelly = (result_value - Decimal(1.0)) / (odd.odd_value - Decimal(1.0))
                        if sandbox:
                            forecast_ins.append(ForecastSandbox(
                                                                forecast_set_id=forecast_set.id,
                                                                match_id=match.id,
                                                                odd_id=odd.id,
                                                                predictor_id=self.id,
                                                                match_date=match.match_date,
                                                                harvest_id=self.harvest_id,
                                                                success_chance=success_chance,
                                                                lose_chance=lose_chance,
                                                                result_value=result_value,
                                                                kelly=kelly)
                                            )
                        else:
                            if ins:
                                forecast_ins.append(Forecast(
                                                            forecast_set_id=forecast_set.id,
                                                            match_id=match.id,
                                                            odd_id=odd.id,
                                                            predictor_id=self.id,
                                                            match_date=match.match_date,
                                                            harvest_id=self.harvest_id,
                                                            success_chance=success_chance,
                                                            lose_chance=lose_chance,
                                                            result_value=result_value,
                                                            kelly=kelly,
                                                            status=Forecast.SETTLED if odd.status==Odd.FINISHED else Forecast.UNSETTLED
                                                            )
                                                )
                            elif upd:
                                forecast_old.success_chance=success_chance
                                forecast_old.lose_chance=lose_chance
                                forecast_old.result_value=result_value
                                forecast_old.kelly=kelly
                                forecast_old.status=Forecast.SETTLED if odd.status==Odd.FINISHED else Forecast.UNSETTLED
                                forecast_upd.append(forecast_old)


                if forecast_ins:
                    if sandbox:
                        ForecastSandbox.objects.bulk_create(forecast_ins)
                    else:
                        Forecast.objects.bulk_create(forecast_ins)
                if forecast_upd:
                    if sandbox:
                        ForecastSandbox.objects.bulk_update(forecast_upd, ["success_chance","lose_chance","result_value","kelly","status"])
                    else:
                        Forecast.objects.bulk_update(forecast_upd, ["success_chance","lose_chance","result_value","kelly","status"])

    def forecasting_odd(self, odd):
        from .harvest import TeamSkill
        predictor = self.get_real_predictor()

        predictor.period = odd.period
        predictor.value_type_slug = odd.value_type.slug
        predictor.value_type = odd.value_type

        predictor.skill_h = TeamSkill.get_team_skill(predictor.harvest, 
                                                     odd.match.team_h, 
                                                     odd.match.match_date, 
                                                     odd.match, 
                                                     param="h")
        predictor.skill_a = TeamSkill.get_team_skill(predictor.harvest, 
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
        (PREPARED, 'Preapred'),
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


    def api_update_match_xG(self, harvest, match, xG_h, xA_h, G_h, A_h, xG_a, xA_a, G_a, A_a):
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
                self.forecast_match(match)

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


    def preapre_sandbox(self, match, harvest):
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
                                            kelly = f.kelly
                                        ) for f in Forecast.objects.filter(forecast_set_id=self.id, match_id=match.id)]
            ForecastSandbox.objects.bulk_create(forecasts)
            


    def restore_forecast(self, match, harvest):
        TeamSkillSandbox.objects.filter(forecast_set=self, 
                                        harvest=harvest,
                                        team=match.team_h, 
                                        event_date=match.match_date, 
                                        param='h').delete()
        TeamSkillSandbox.objects.filter(forecast_set=self, 
                                        harvest=harvest,
                                        team=match.team_a, 
                                        event_date=match.match_date, 
                                        param='a').delete()
        ForecastSandbox.objects.filter(forecast_set=self, match=match).delete()
        self.preapre_sandbox(match, harvest)


    def forecasting(self, delete_old=False):
        start_time = datetime.now()

        for m in TeamSkillSandbox.objects.filter(forecast_set=self).order_by("match_id").distinct("match_id"): 
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
            print("predictor", predictor)
            real_predictor = predictor.get_real_predictor()
            real_predictor.forecasting(self)

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

    def forecast_match(self, match):
        ForecastSandbox.objects.filter(forecast_set=self, match=match).delete()
        for predictor in Predictor.objects.filter(status=Predictor.ACTIVE).order_by("priority", "pk"):
            real_predictor = predictor.get_real_predictor()
            real_predictor.forecasting(self, match_id=match.id, sandbox=True)



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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["forecast_set", "match", "odd", "predictor" ], name='unique_forecast_sandbox'),
        ]

    def __str__(self):
        return f'Set:{self.forecast_set},M:<{self.match},{self.match_date}>,Odd:<{self.odd}>,P:{self.predictor},R:{round(self.result_value,4)},S:{round(self.success_chance,4)}'




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

class PredictorOrigDistrXG(Mixins.OriginalDataExtraction, Mixins.FixedDistributionForecastingEx, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-distr-copy"

class PredictorStdDistrXG(Mixins.StandartExtraction, Mixins.FixedDistributionForecastingEx, Predictor):
    class Meta:
        proxy = True
    def get_distribution_slug(self):
        return "xg-ext-distr-copy"
