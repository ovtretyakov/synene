from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.query import RawQuerySet
from django.db.models import sql, F, Q, Count, Max
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber

from background_task import background
from graphos.sources.model import ModelDataSource
from graphos.renderers import gchart

import urllib.parse
from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string, SimpleRawQuerySet
from project.core.models import Sport, League, Match, LoadSource, Team
from ..models import (HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague,
                     ForecastHandler, Predictor, ForecastSet,
                     Forecast, TeamSkill, ForecastSandbox, TeamSkillSandbox,
                     Odd, ValueType, BetType)
from ..forms import (HarvestHandlerForm, HarvestHandlerDeleteForm,
                     HarvestForm, HarvestDeleteForm, HarvestDoHarvestForm, HarvestDoHarvestAllForm,
                     HarvestConfigForm, HarvestConfigDeleteForm,
                     HarvestGroupForm, HarvestGroupDeleteForm, HarvestGroupDoHarvestForm,
                     HarvestLeagueForm, HarvestLeagueDeleteForm,
                     ForecastHandlerForm, ForecastHandlerDeleteForm,
                     PredictorForm, PredictorDeleteForm,
                     ForecastSetForm, ForecastSetDeleteForm,
                     MatchXGForm, RestoreMatchXGForm
                     )
from ..serializers import (HarvestHandlerSerializer, HarvestSerializer, HarvestConfigSerializer, HarvestGroupSerializer,
                           ForecastHandlerSerializer, PredictorSerializer, ForecastSetSerializer,
                           ForecastMatchesSerializer, ForecastSerializer, PreviousMatchesSerializer,
                           SeasonChartSerializer
                           )


@background
def forecast_set_create(slug, name, keep_only_best_int, only_finished_int, start_date_str):
    keep_only_best = (keep_only_best_int==1)
    only_finished = (only_finished_int==1)
    start_date = get_date_from_string(start_date_str)
    ForecastSet.api_create(slug=slug, name=name, keep_only_best=keep_only_best, only_finished=only_finished, start_date=start_date)

@background
def forecast_set_update(forecast_set_pk, slug, name, keep_only_best_int, only_finished_int, start_date_str):
    keep_only_best = (keep_only_best_int==1)
    only_finished = (only_finished_int==1)
    start_date = get_date_from_string(start_date_str)
    forecast_set = ForecastSet.objects.get(pk=forecast_set_pk)
    forecast_set.api_update(slug=slug, name=name, keep_only_best=keep_only_best, only_finished=only_finished, start_date=start_date)


####################################################
#  HarvestHandler
####################################################
class HarvestHandlerView(generic.TemplateView):
    template_name = "betting/harvest_handler_list.html"


class HarvestHandlerAPI(ListAPIView):
    serializer_class = HarvestHandlerSerializer
    queryset = HarvestHandler.objects.all()
    lookup_field = "pk"


class HarvestHandlerCreateView(BSModalCreateView):
    model = HarvestHandler
    form_class = HarvestHandlerForm
    template_name = 'betting/create_harvest_handler.html'
    success_message = "Success: Harvest handler was created."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestHandlerUpdateView(BSModalUpdateView):
    model = HarvestHandler
    form_class = HarvestHandlerForm
    template_name = 'betting/update_harvest_handler.html'
    success_message = "Success: Harvest handler was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestHandlerDeleteView(BSModalCreateView):
    model = HarvestHandler
    form_class = HarvestHandlerDeleteForm
    template_name = 'betting/delete_harvest_handler.html'
    success_message = "Success: Harvest handler was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestHandlerDeleteView, self).get_context_data(**kwargs)

        # pk = self.request.GET.get("pk", None)
        pk = self.kwargs['pk']
        if pk:
            object = HarvestHandler.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return reverse_lazy("betting:harvest_handler_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = HarvestHandler.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  Harvest
####################################################
class HarvestView(generic.TemplateView):
    template_name = "betting/harvest_list.html"

class HarvestAPI(ListAPIView):
    serializer_class = HarvestSerializer
    queryset = Harvest.objects.all()
    lookup_field = "pk"

class HarvestCreateView(BSModalCreateView):
    model = Harvest
    form_class = HarvestForm
    template_name = 'betting/create_harvest.html'
    success_message = "Success: Harvestor was created."

    def get_initial(self):
        football = get_object_or_404(Sport, slug=Sport.FOOTBALL)
        return {
            'sport':football,
        }

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestUpdateView(BSModalUpdateView):
    model = Harvest
    form_class = HarvestForm
    template_name = 'betting/update_harvest.html'
    success_message = "Success: Harvester was updated."

    def get_success_url(self):
        return reverse_lazy("betting:harvest_list")


class HarvestDeleteView(BSModalCreateView):
    model = Harvest
    form_class = HarvestDeleteForm
    template_name = 'betting/delete_harvest.html'
    success_message = "Success: Harvestor was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestDeleteView, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        if pk:
            object = Harvest.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = Harvest.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class HarvestDoHarvestView(BSModalUpdateView):
    model = Harvest
    template_name = "betting/do_harvest_harvest.html"
    form_class = HarvestDoHarvestForm
    success_message = "Success harvesting"
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                harvest_date = cleaned_data["harvest_date"]
                self.object.api_do_harvest(harvest_date)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Harvesting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class HarvestDoHarvestAllView(BSModalCreateView):
    template_name = "betting/do_harvest_harvest_all.html"
    form_class = HarvestDoHarvestAllForm
    success_message = "Success harvesting"
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                harvest_date = cleaned_data["harvest_date"]
                Harvest.api_do_harvest_all(harvest_date)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Harvesting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

####################################################
#  Harvest Config
####################################################
class HarvestConfigAPI(ListAPIView):
    serializer_class = HarvestConfigSerializer
    queryset = HarvestConfig.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        harvest = self.kwargs.get("harvest",0)
        queryset = HarvestConfig.objects.all()
        if harvest:
            queryset = queryset.filter(harvest=harvest)
        return queryset


class HarvestConfigCreateView(BSModalCreateView):
    model = HarvestConfig
    form_class = HarvestConfigForm
    template_name = 'betting/create_harvest_config.html'
    success_message = "Success: Configuration parameter was added."

    def get_initial(self):
        harvest = get_object_or_404(Harvest, pk=self.kwargs['harvest'])
        return {'harvest':harvest,}

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

class HarvestConfigDeleteView(BSModalCreateView):
    model = HarvestConfig
    form_class = HarvestConfigDeleteForm
    template_name = 'betting/delete_harvest_config.html'
    success_message = "Success: Configuration parameter was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestConfigDeleteView, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        if pk:
            object = HarvestConfig.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = HarvestConfig.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



####################################################
#  Harvest Group
####################################################

class HarvestGroupRawQuerySet(RawQuerySet):
    def count(self, *args, **kwargs):
        lst = list(sql.RawQuery(sql=self.raw_query, using=self.db, params=self.params))
        return len(lst)
    # def order_by(self, *args, **kwargs):
    #     return ""


class HarvestGroupAPI(ListAPIView):
    serializer_class = HarvestGroupSerializer
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):
        harvest_id = self.kwargs.get("harvest",0)
        sql = """ 
              SELECT id, 
                       CASE WHEN type = 1 THEN slug0 ELSE '' END AS slug, 
                       name, harvest_id, country_id, status, harvest_date, last_update, country_name, type
                  FROM  
                    (
                      SELECT g.id, g.slug AS slug0, g.name, g.harvest_id, g.country_id, g.status, g.harvest_date, g.last_update, 
                             c.name AS country_name, 1 AS type
                        FROM synene.betting_harvestgroup g JOIN synene.core_country c ON(g.country_id = c.id)
                        WHERE g.harvest_id = %s
                      UNION ALL
                      SELECT hl.id, g.slug AS slug0, l.name, g.harvest_id, NULL AS country_id, NULL AS status, NULL AS harvest_date, NULL AS last_update, 
                             '' AS country_name, 2 AS type
                        FROM synene.betting_harvestgroup g 
                             JOIN synene.betting_harvestleague hl ON(g.id = hl.harvest_group_id)
                             JOIN synene.core_league l ON(hl.league_id = l.id)
                        WHERE g.harvest_id = %s
                     ) d
                  ORDER BY slug0, type

              """
        # queryset = HarvestGroup.objects.raw(sql, [harvest_id, harvest_id,])
        queryset = HarvestGroupRawQuerySet(sql, params=[harvest_id, harvest_id,], model=HarvestGroup)
        return queryset


class HarvestGroupCreateView(BSModalCreateView):
    model = HarvestGroup
    form_class = HarvestGroupForm
    template_name = 'betting/create_harvest_group.html'
    success_message = "Success: Harvestor group was created."

    def get_initial(self):
        harvest = get_object_or_404(Harvest, pk=self.kwargs['harvest'])
        return {'harvest':harvest,}

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestGroupUpdateView(BSModalUpdateView):
    model = HarvestGroup
    form_class = HarvestGroupForm
    template_name = 'betting/update_harvest_group.html'
    success_message = "Success: Harvester group was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestGroupDeleteView(BSModalCreateView):
    model = HarvestGroup
    form_class = HarvestGroupDeleteForm
    template_name = 'betting/delete_harvest_group.html'
    success_message = "Success: Harvestor group was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestGroupDeleteView, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        if pk:
            object = HarvestGroup.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = HarvestGroup.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class HarvestGroupDoHarvestView(BSModalUpdateView):
    model = HarvestGroup
    template_name = "betting/do_harvest_harvest_group.html"
    form_class = HarvestGroupDoHarvestForm
    success_message = "Success harvesting"
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                harvest_date = cleaned_data["harvest_date"]
                self.object.api_do_harvest(harvest_date)
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Harvesting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  Harvest League
####################################################

class HarvestLeagueCreateView(BSModalCreateView):
    model = HarvestLeague
    form_class = HarvestLeagueForm
    template_name = 'betting/create_harvest_league.html'
    success_message = "Success: Harvestor group was created."

    def get_initial(self):
        harvest_group = get_object_or_404(HarvestGroup, pk=self.kwargs['harvest_group'])
        return {'harvest_group':harvest_group,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestLeagueCreateView, self).get_context_data(**kwargs)

        harvest_group = self.kwargs['harvest_group']
        if harvest_group:
            harvest_group = HarvestGroup.objects.get(pk=harvest_group)
            context["hgroup"] = harvest_group

        return context    


    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class HarvestLeagueDeleteView(BSModalCreateView):
    model = HarvestLeague
    form_class = HarvestLeagueDeleteForm
    template_name = 'betting/delete_harvest_league.html'
    success_message = "Success: League was removed from group."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(HarvestLeagueDeleteView, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        if pk:
            object = HarvestLeague.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = HarvestLeague.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  ForecastHandler
####################################################
class ForecastHandlerView(generic.TemplateView):
    template_name = "betting/forecast_handler_list.html"


class ForecastHandlerAPI(ListAPIView):
    serializer_class = ForecastHandlerSerializer
    queryset = ForecastHandler.objects.all()
    lookup_field = "pk"


class ForecastHandlerCreateView(BSModalCreateView):
    model = ForecastHandler
    form_class = ForecastHandlerForm
    template_name = 'betting/create_forecast_handler.html'
    success_message = "Success: Forecast handler was created."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class ForecastHandlerUpdateView(BSModalUpdateView):
    model = ForecastHandler
    form_class = ForecastHandlerForm
    template_name = 'betting/update_forecast_handler.html'
    success_message = "Success: Forecast handler was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class ForecastHandlerDeleteView(BSModalCreateView):
    model = ForecastHandler
    form_class = ForecastHandlerDeleteForm
    template_name = 'betting/delete_forecast_handler.html'
    success_message = "Success: Forecast handler was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ForecastHandlerDeleteView, self).get_context_data(**kwargs)

        # pk = self.request.GET.get("pk", None)
        pk = self.kwargs['pk']
        if pk:
            object = ForecastHandler.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return reverse_lazy("betting:forecast_handler_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = ForecastHandler.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  Predictor
####################################################
class PredictorView(generic.TemplateView):
    template_name = "betting/predictor_list.html"


class PredictorAPI(ListAPIView):
    serializer_class = PredictorSerializer
    queryset = Predictor.objects.all()
    lookup_field = "pk"


class PredictorCreateView(BSModalCreateView):
    model = Predictor
    form_class = PredictorForm
    template_name = 'betting/create_predictor.html'
    success_message = "Success: Predictor was created."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class PredictorUpdateView(BSModalUpdateView):
    model = Predictor
    form_class = PredictorForm
    template_name = 'betting/update_predictor.html'
    success_message = "Success: Predictor was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class PredictorDeleteView(BSModalCreateView):
    model = Predictor
    form_class = PredictorDeleteForm
    template_name = 'betting/delete_predictor.html'
    success_message = "Success: Predictor was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(PredictorDeleteView, self).get_context_data(**kwargs)

        # pk = self.request.GET.get("pk", None)
        pk = self.kwargs['pk']
        if pk:
            object = Predictor.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return reverse_lazy("betting:predictor_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = Predictor.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  ForecastSet
####################################################
class ForecastSetView(generic.TemplateView):
    template_name = "betting/forecast_set_list.html"


class ForecastSetAPI(ListAPIView):
    serializer_class = ForecastSetSerializer
    queryset = ForecastSet.objects.all()
    lookup_field = "pk"


class ForecastSetCreateView(BSModalCreateView):
    model = ForecastSet
    form_class = ForecastSetForm
    template_name = 'betting/create_forecast_set.html'
    success_message = 'Success: Creating "Forecast set" id queued.'

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data

                start_date = cleaned_data["start_date"]
                start_date_str = ""
                if start_date:
                    start_date_str = start_date.strftime('%d.%m.%Y')

                forecast_set_create(
                                        slug=cleaned_data["slug"], 
                                        name=cleaned_data["name"], 
                                        keep_only_best_int=1 if cleaned_data["keep_only_best"] else 0, 
                                        only_finished_int=1 if cleaned_data["only_finished"] else 0, 
                                        start_date_str=start_date_str,
                                        verbose_name = 'Do ' + cleaned_data["name"]
                                        )
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Creating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class ForecastSetUpdateView(BSModalUpdateView):
    model = ForecastSet
    form_class = ForecastSetForm
    template_name = 'betting/update_forecast_set.html'
    success_message = 'Success: Updating "Forecast set" id queued.'

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data

                start_date = cleaned_data["start_date"]
                start_date_str = ""
                if start_date:
                    start_date_str = start_date.strftime('%d.%m.%Y')

                forecast_set_update(
                                        forecast_set_pk=self.object.pk,
                                        slug=cleaned_data["slug"], 
                                        name=cleaned_data["name"], 
                                        keep_only_best_int=1 if cleaned_data["keep_only_best"] else 0, 
                                        only_finished_int=1 if cleaned_data["only_finished"] else 0, 
                                        start_date_str=start_date_str,
                                        verbose_name = 'Do ' + cleaned_data["name"]
                                        )
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class ForecastSetDeleteView(BSModalCreateView):
    model = ForecastSet
    form_class = ForecastSetDeleteForm
    template_name = 'betting/delete_forecast_set.html'
    success_message = "Success: Forecast set was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ForecastSetDeleteView, self).get_context_data(**kwargs)

        # pk = self.request.GET.get("pk", None)
        pk = self.kwargs['pk']
        if pk:
            object = ForecastSet.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return reverse_lazy("betting:forecast_set_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = ForecastSet.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  ForecastMatches
####################################################
class ForecastMatchesView(generic.TemplateView):
    template_name = "betting/forecast_match_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ForecastMatchesView, self).get_context_data(**kwargs)

        forecast_set_id = self.kwargs['forecast_set']
        if forecast_set_id:
            context["forecast_set_id"] = forecast_set_id

        leagues = (Forecast.objects.filter(forecast_set=forecast_set_id)
                                   .values(league_id=F("match__league__id"),
                                           league_name=F("match__league__name"),
                                           country_name=F("match__league__country__name")
                                          )
                                   .distinct()
                  )

        # leagues = League.objects.all()
        context["leagues"] = leagues

        load_statuses = (("A", "All"),) + Match.STATUS_CHOICES
        context["statuses"] = load_statuses

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_league = self.request.GET.get("selected_league", None)
        if selected_league:
            context["selected_league"] = int(selected_league)
        selected_status = self.request.GET.get("status", None)
        if selected_status:
            context["selected_status"] = selected_status
        else:
            context["selected_status"] = "A"

        return context    



class ForecastMatchesAPI(ListAPIView):
    serializer_class = ForecastMatchesSerializer

    def get_queryset(self, *args, **kwargs):
        forecast_set_id = self.kwargs.get("forecast_set",0)

        queryset = Forecast.objects.filter(forecast_set=forecast_set_id)

        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(match_date__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(match_date__lte=date_to)
        selected_status = self.request.query_params.get("selected_status", None)
        if selected_status and selected_status != "A":
            queryset = queryset.filter(match__status=selected_status)
        selected_league = self.request.query_params.get("selected_league", None)
        if selected_league and selected_league != "0":
            selected_league = int(selected_league)
            print("!!!! selected_league",selected_league)
            queryset = queryset.filter(match__league=selected_league)

        queryset = (queryset.values(
                             "match_date",
                             "match_id",
                             league_name=F("match__league__name"), 
                             name_h=F("match__team_h__name"), 
                             name_a=F("match__team_a__name"), 
                             match_status=F("match__status"), 
                             match_score=F("match__score"), 
                             ) 
                     .annotate(odds=Count("odd", distinct=True),
                               odds_plus=Count("odd", distinct=True, filter=Q(result_value__gt=1)),
                               best_chance=Max("success_chance"),
                               best_result_value=Max("result_value"),
                               best_kelly=Max("kelly"),
                              )
                    )
        return queryset




class ForecastMatchDetail(BSModalReadView):
    model = Match
    template_name = 'betting/detail_forecast_match.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        forecast_set_id = self.kwargs['forecast_set']
        forecast_set = ForecastSet.objects.get(pk=forecast_set_id)
        if forecast_set_id:
            context["forecast_set_id"] = forecast_set_id
        context["match_id"] = self.object.pk

        harvest = Harvest.objects.get(slug="hg-0")
        forecast_set.preapre_sandbox(match=self.object, harvest=harvest)
        xG_h0_skill = TeamSkillSandbox.objects.get(harvest=harvest, team=self.object.team_h, event_date=self.object.match_date, param="h")
        xG_a0_skill = TeamSkillSandbox.objects.get(harvest=harvest, team=self.object.team_a, event_date=self.object.match_date, param="a")
        # xG_h0_skill = TeamSkill.get_team_skill(harvest=harvest, team=self.object.team_h, skill_date=self.object.match_date, param="h")
        # xG_a0_skill = TeamSkill.get_team_skill(harvest=harvest, team=self.object.team_a, skill_date=self.object.match_date, param="a")


        context["xG_h"] = self.object.get_stat("xg", "h", 0)
        context["xG_a"] = self.object.get_stat("xg", "a", 0)
        if xG_h0_skill and xG_a0_skill:
            context["fxG_h"] = round(xG_h0_skill.value1*xG_a0_skill.value2,3)
            context["fxG_a"] = round(xG_a0_skill.value1*xG_h0_skill.value2,3)
            context["fG_h"]  = round(xG_h0_skill.value9*xG_a0_skill.value10,3)
            context["fG_a"]  = round(xG_a0_skill.value9*xG_h0_skill.value10,3)

            context["xG_h_skill"] = round(xG_h0_skill.value1,3)
            context["xA_h_skill"] = round(xG_h0_skill.value2,3)
            context["kG_h_skill"] = round(xG_h0_skill.value3,3)
            context["kA_h_skill"] = round(xG_h0_skill.value4,3)
            context["G_h_skill"]  = round(xG_h0_skill.value9,3)
            context["A_h_skill"]  = round(xG_h0_skill.value10,3)

            context["xG_a_skill"] = round(xG_a0_skill.value1,3)
            context["xA_a_skill"] = round(xG_a0_skill.value2,3)
            context["kG_a_skill"] = round(xG_a0_skill.value3,3)
            context["kA_a_skill"] = round(xG_a0_skill.value4,3)
            context["G_a_skill"]  = round(xG_a0_skill.value9,3)
            context["A_a_skill"]  = round(xG_a0_skill.value10,3)

        # odd filter
        context["bookies"] = Forecast.objects.filter(forecast_set=forecast_set_id,
                                                     match = self.object
                                                     ).values(
                                                                bookie_id=F("odd__bookie__id"),
                                                                bookie_name=F("odd__bookie__name")
                                                                ).distinct().order_by("bookie_id")
        context["results"] = (("a", "All results"),) + Odd.RESULT_CHOICES
        context["sections"] = ValueType.objects.all().order_by("name")
        context["types"] = BetType.objects.all().order_by("name")
        context["predictors"] = Forecast.objects.filter(forecast_set=forecast_set_id,
                                                        match = self.object
                                                        ).values(
                                                                pred_id=F("predictor__id"),
                                                                pred_name=F("predictor__name")
                                                                ).distinct().order_by("pred_id")

        Predictor.objects.all().order_by("pk")

        selected_predictor = self.request.GET.get("predictor", None)
        if selected_predictor:
            context["selected_predictor"] = int(selected_predictor)
        selected_bookie = self.request.GET.get("bookie", None)
        if selected_bookie == None:
            selected_bookie = 0
        context["selected_bookie"] = int(selected_bookie)
        selected_section = self.request.GET.get("section", None)
        if selected_section:
            context["selected_section"] = int(selected_section)
        bet_types = self.request.GET.get("bet_types", None)
        bet_types_info = "All types"
        if bet_types:
            bet_types_len = len(bet_types.split(","))
            if bet_types_len == 1:
                bet_types_info = "1 type"
            elif bet_types_len > 1:
                bet_types_info = str(bet_types_len) + " types"
            context["bet_types"] = bet_types
        context["bet_types_info"] = bet_types_info
        expect = self.request.GET.get("expect", None)
        if expect == None or expect == "":
            expect = 0.98
        context["expect"] = expect
        per = self.request.GET.get("per", None)
        if per:
            context["per"] = per
        odd_from = self.request.GET.get("odd_from", None)
        if odd_from:
            context["odd_from"] = odd_from
        odd_to = self.request.GET.get("odd_to", None)
        if odd_to:
            context["odd_to"] = odd_to
        selected_team = self.request.GET.get("team", None)
        if selected_team:
            context["selected_team"] = selected_team
        else:
            context["selected_team"] = "all"
        par = self.request.GET.get("par", None)
        if par:
            context["par"] = par
            context["par_encoding"] = urllib.parse.quote(par) #par.replace("+", "%2B")
        selected_result = self.request.GET.get("result", None)
        if selected_result:
            context["selected_result"] = selected_result
        else:
            context["selected_result"] = "a"

        harvest_id = 0
        harvest = Harvest.get_xg_harvest()
        if harvest:
            harvest_id = harvest.pk

        sql = """
                SELECT *
                  FROM 
                    (
                    SELECT s.*,
                           row_number() OVER(ORDER BY event_date DESC) AS rn
                      FROM betting_teamskill s
                      WHERE harvest_id = %s AND team_id = %s AND event_date < %s AND param = %s
                    ) d
                  WHERE rn <= 10
                  ORDER BY event_date
              """
        fields = ["event_date", "value1", "value2", "value9", "value10"]
        headers = ["Date", "xG", "xA", "G", "A"]
        options={'title': "xG skills",
                 'colors': ['green', 'red', 'green', 'red'],
                 'series': { 2: {'lineDashStyle':[4, 4]}, 3: {'lineDashStyle':[4, 4]}},
                 'chartArea':{'left':30,'width':'80%',}
                 }
        chart_width = 650
        h_chart = gchart.LineChart(ModelDataSource(queryset=
                                                     TeamSkill.objects.raw(sql, 
                                                                           [harvest_id, self.object.team_h.pk, self.object.match_date, 'h']
                                                                           ), 
                                                   fields=fields,
                                                   headers=headers,
                                                   ),
                                   options=options
                                   )
        h_chart.width = chart_width
        a_chart = gchart.LineChart(ModelDataSource(queryset=
                                                     TeamSkill.objects.raw(sql, 
                                                                           [harvest_id, self.object.team_a.pk, self.object.match_date, 'a']
                                                                           ), 
                                                   fields=fields,
                                                   headers=headers,
                                                   ),
                                   options=options
                                   )
        a_chart.width = chart_width
        context["h_chart"] = h_chart
        context["a_chart"] = a_chart

        return context    


class ForecastAPI(ListAPIView):
    serializer_class = ForecastSerializer

    def get_queryset(self, *args, **kwargs):
        forecast_set_id = self.kwargs.get("forecast_set",0)
        match_id = self.kwargs.get("match",0)

        queryset = (ForecastSandbox.objects
                            .filter(forecast_set=forecast_set_id, match=match_id)
                            .annotate(growth=(1-F("kelly")+F("kelly")*F("result_value")))
                    )
        # queryset = Forecast.objects.filter(forecast_set=forecast_set_id, match=match_id)

        selected_bookie = self.request.query_params.get("selected_bookie", None)
        if selected_bookie and int(selected_bookie) > 0:
            queryset = queryset.filter(odd__bookie_id=selected_bookie)
        selected_section = self.request.query_params.get("selected_section", None)
        if selected_section and int(selected_section) > 0:
            queryset = queryset.filter(odd__value_type_id=selected_section)
        bet_types = self.request.query_params.get("bet_types", None)
        if bet_types:
            queryset = queryset.filter(odd__bet_type_id__in=bet_types.split(","))
        per = self.request.query_params.get("per", None)
        if per:
            queryset = queryset.filter(odd__period=per)
        odd_from = self.request.query_params.get("odd_from", None)
        if odd_from:
            queryset = queryset.filter(odd__odd_value__gte=odd_from)
        odd_to = self.request.query_params.get("odd_to", None)
        if odd_to:
            queryset = queryset.filter(odd__odd_value__lte=odd_to)
        selected_team = self.request.query_params.get("selected_team", None)
        if selected_team:
            if selected_team in("h","a"):
                queryset = queryset.filter(odd__team=selected_team)
            elif selected_team == "empty":
                queryset = queryset.filter(odd__team="")
        par = self.request.query_params.get("par", None)
        if par:
            queryset = queryset.filter(odd__param=par)
        selected_result = self.request.query_params.get("selected_result", None)
        if selected_result and selected_result != "a":
            queryset = queryset.filter(odd__result=selected_result)
        expect = self.request.query_params.get("expect", None)
        if expect:
            queryset = queryset.filter(result_value__gte=expect)
        selected_predictor = self.request.query_params.get("selected_predictor", None)
        if selected_predictor and int(selected_predictor) > 0:
            queryset = queryset.filter(predictor_id=selected_predictor)

        queryset = queryset.annotate(odd_status=F("odd__result"))
        return queryset




class PreviousMatchesAPI(ListAPIView):
    serializer_class = PreviousMatchesSerializer
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):

        match_id = self.kwargs.get("match",0)
        team = self.kwargs.get("team",0)
        team_id = 0
        match_date = None
        league_id = 0
        if match_id:
            match = Match.objects.filter(pk=match_id).first()
            if match:
                team_id = match.team_h.pk if team == 'h' else match.team_a.pk
                match_date = match.match_date
                league_id = match.league.pk

        harvest_id = 0
        harvest = Harvest.get_xg_harvest()
        if harvest:
            harvest_id = harvest.pk

        sql = """ 
                    WITH m AS 
                      (
                        SELECT *
                          FROM 
                            (
                            SELECT d.*, ROW_NUMBER() OVER(ORDER BY match_date DESC, match_id DESC) AS rn
                              FROM 
                                (
                            SELECT m.result, 
                                   'h' AS ha, m.id AS match_id, m.match_date, m.score, m.team_h_id, m.team_a_id, 
                                   h.name AS h_name, a.name AS a_name, 
                                   TO_NUMBER(gh.value,'99999999.9999') AS gxH,
                                   TO_NUMBER(ga.value,'99999999.9999') AS gxA
                              FROM core_match m
                                   JOIN core_matchstats gh 
                                     ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
                                   JOIN core_matchstats ga 
                                     ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
                                   JOIN core_team h ON (m.team_h_id = h.id)
                                   JOIN core_team a ON (m.team_a_id = a.id)
                              WHERE m.league_id = %s AND m.match_date < %s AND m.team_h_id = %s
                                AND m.status = 'F'
                            UNION ALL
                            SELECT CASE WHEN m.result='w' THEN 'l' WHEN m.result='l' THEN 'w' ELSE m.result END AS result, 
                                   'a' AS ha, m.id AS match_id, m.match_date, m.score, m.team_h_id, m.team_a_id,
                                   h.name AS h_name, a.name AS a_name, 
                                   TO_NUMBER(gh.value,'99999999.9999') AS gxH,
                                   TO_NUMBER(ga.value,'99999999.9999') AS gxA
                              FROM core_match m
                                   JOIN core_matchstats gh 
                                     ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
                                   JOIN core_matchstats ga 
                                     ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
                                   JOIN core_team h ON (m.team_h_id = h.id)
                                   JOIN core_team a ON (m.team_a_id = a.id)
                              WHERE m.league_id = %s AND m.match_date < %s AND m.team_a_id = %s
                                AND m.status = 'F'
                                ) d
                            ) d2
                          WHERE rn <= 10
                      ),
                    mh AS 
                      (
                        SELECT *
                          FROM 
                            (
                            SELECT m.*,
                                   sh.value1 AS hv1, sh.value2 AS hv2, sh.value9 AS hv9, sh.value10 AS hv10,
                                   row_number() OVER(PARTITION BY m.match_id ORDER BY sh.event_date DESC, sh.match_id DESC)  AS rnh
                              FROM m 
                                   JOIN betting_teamskill sh
                                     ON(sh.harvest_id = %s AND 
                                        sh.team_id = m.team_h_id AND 
                                        sh.param = 'h' AND 
                                        sh.event_date < m.match_date 
                                        AND sh.match_cnt > 3
                                        )
                            ) d
                          WHERE rnh = 1
                      ),
                    ma AS 
                      (
                        SELECT d.*,
                               hv1*av2 AS gxH1, av1*hv2 AS gxA1, hv9*av10 AS gxH1, av9*hv10 AS gxA2,
                               ROUND(hv1*av2,3) AS ph1, ROUND(av1*hv2,3) AS pa1, ROUND(hv9*av10,3) AS ph2, ROUND(av9*hv10,3) AS pa2
                          FROM 
                            (
                            SELECT mh.*,
                                   sh.value1 AS av1, sh.value2 AS av2, sh.value9 AS av9, sh.value10 AS av10,
                                   row_number() OVER(PARTITION BY mh.match_id ORDER BY sh.event_date DESC, sh.match_id DESC) AS rna
                              FROM mh 
                                   JOIN betting_teamskill sh
                                       ON(sh.harvest_id = %s AND 
                                          sh.team_id = mh.team_a_id AND 
                                          sh.param = 'a' AND 
                                          sh.event_date < mh.match_date 
                                          AND sh.match_cnt > 3
                                          )
                            ) d
                          WHERE rna = 1
                      )
                    SELECT match_id AS id, result, ha, match_date, score, team_h_id, team_a_id, h_name, a_name,
                           gxH::text || '-' || gxA::text  AS gx,
                           ph1::text || '-' || pa1::text  AS fore_gx,
                           ph2::text || '-' || pa2::text  AS fore_g
                      FROM ma
                      ORDER BY match_date DESC, match_id DESC
              """
        params  = [league_id, match_date, team_id,
                   league_id, match_date, team_id,
                   harvest_id, harvest_id,
                   ]      
        queryset = SimpleRawQuerySet(sql, params=params, model=Match)
        return queryset





class SeasonChartAPI(ListAPIView):
    serializer_class = SeasonChartSerializer
    lookup_field = "id"

    def get_queryset(self, *args, **kwargs):

        match_id = self.kwargs.get("match",0)
        season_id = 0
        match_date = None
        league_id = 0
        if match_id:
            match = Match.objects.filter(pk=match_id).first()
            if match:
                season_id = match.season.pk
                match_date = match.match_date
                league_id = match.league.pk

        sql = """ 
                WITH m AS 
                  (
                    SELECT m.id AS match_id, m.*, 
                           h.name AS h_name, a.name AS a_name, l.name AS league_name,
                           TO_NUMBER(s1.value,'99999999.9999') AS gH,
                           TO_NUMBER(s2.value,'99999999.9999') AS gA,
                           TO_NUMBER(gh.value,'99999999.9999') AS gxH,
                           TO_NUMBER(ga.value,'99999999.9999') AS gxA
                      FROM core_match m
                           JOIN core_matchstats s1 
                             ON(s1.stat_type = 'g' AND s1.period = 0 AND s1.match_id = m.id AND s1.competitor = 'h' )
                           JOIN core_matchstats s2 
                             ON(s2.stat_type = 'g' AND s2.period = 0 AND s2.match_id = m.id AND s2.competitor = 'a')
                           JOIN core_matchstats gh 
                             ON(gh.stat_type = 'xg' AND gh.period = 0 AND gh.match_id = m.id AND gh.competitor = 'h')
                           JOIN core_matchstats ga 
                             ON(ga.stat_type = 'xg' AND ga.period = 0 AND ga.match_id = m.id AND ga.competitor = 'a')
                           JOIN core_team h 
                             ON (m.team_h_id = h.id)
                           JOIN core_team a 
                             ON (m.team_a_id = a.id)
                           JOIN core_league l 
                             ON (m.league_id = l.id)
                      WHERE m.league_id = %s AND m.season_id = %s AND m.match_date < %s
                        AND m.status = 'F'
                  ),
                t AS (
                  SELECT m.team_h_id AS team_id, h_name AS team_name, 
                         result, 
                         gH, gA
                    FROM m
                  UNION ALL
                  SELECT m.team_a_id AS team_id, a_name AS team_name, 
                         CASE WHEN result = 'w' THEN 'l' WHEN result = 'l' THEN 'w' ELSE result END AS result, 
                         gA, gH
                    FROM m
                ),
                agg AS (
                  SELECT team_id, team_name,
                         COUNT(*) AS match_cnt, SUM(gH) AS gH, SUM(gA) AS gA,
                         COUNT(*) FILTER(WHERE result='w') AS w,
                         COUNT(*) FILTER(WHERE result='d') AS d,
                         COUNT(*) FILTER(WHERE result='l') AS l,
                         SUM(CASE WHEN result='w' THEN 3 WHEN result='d' THEN 1 ELSE 0 END) AS points 
                    FROM t
                    GROUP BY team_id, team_name
                )
                SELECT  ROW_NUMBER() OVER(ORDER BY points DESC, gH - gA DESC, gH DESC, team_id) AS n,
                        team_id AS id, team_name, match_cnt AS m, w, d, l, gH AS G, gA, points AS pts 
                  FROM agg
                  ORDER BY n
              """
        params  = [league_id, season_id, match_date, 
                   ]      
        queryset = SimpleRawQuerySet(sql, params=params, model=Team)
        return queryset



class MatchXGUpdateView(BSModalUpdateView):
    model = Match
    form_class = MatchXGForm
    template_name = 'betting/update_match_xg.html'
    success_message = "Success: xG values were updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_initial(self, **kwargs):
        forecast_set_id = self.kwargs['forecast_set']
        harvest = Harvest.objects.get(slug="hg-0")
        self.forecast_set_id = forecast_set_id
        self.harvest = harvest
        xG_h0 = TeamSkillSandbox.objects.get(harvest=harvest, team=self.object.team_h, event_date=self.object.match_date, param="h")
        xG_a0 = TeamSkillSandbox.objects.get(harvest=harvest, team=self.object.team_a, event_date=self.object.match_date, param="a")
        init = {
                'xG_h': round(xG_h0.value1,3),
                'xA_h': round(xG_h0.value2,3),
                'G_h':  round(xG_h0.value9,3),
                'A_h':  round(xG_h0.value10,3),
                'xG_a': round(xG_a0.value1,3),
                'xA_a': round(xG_a0.value2,3),
                'G_a':  round(xG_a0.value9,3),
                'A_a':  round(xG_a0.value10,3),
        }
        return init


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        forecast_set_id = self.kwargs['forecast_set']
        context["forecast_set_id"] = forecast_set_id
        context["match_id"] = self.object.pk

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                forecast_set = ForecastSet.objects.get(pk=self.forecast_set_id)
                forecast_set.api_update_match_xG(self.harvest, 
                                                 self.object, 
                                                 cleaned_data["xG_h"], 
                                                 cleaned_data["xA_h"], 
                                                 cleaned_data["G_h"], 
                                                 cleaned_data["A_h"], 
                                                 cleaned_data["xG_a"], 
                                                 cleaned_data["xA_a"], 
                                                 cleaned_data["G_a"], 
                                                 cleaned_data["A_a"]
                                                 )
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



class MatchXGRestoreView(BSModalUpdateView):
    model = Match
    form_class = RestoreMatchXGForm
    template_name = 'betting/restore_match_xg.html'
    success_message = "Success: xG values were restored."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        forecast_set_id = self.kwargs['forecast_set']
        harvest = Harvest.objects.get(slug="hg-0")
        self.harvest = harvest
        self.forecast_set_id = forecast_set_id

        context["forecast_set_id"] = forecast_set_id
        context["match_id"] = self.object.pk

        return context    

    def form_valid(self, form, **kwargs):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                forecast_set_id = self.kwargs['forecast_set']
                harvest = Harvest.objects.get(slug="hg-0")
                cleaned_data = form.cleaned_data
                forecast_set = ForecastSet.objects.get(pk=forecast_set_id)
                forecast_set.api_restore_match_xG(harvest, self.object)
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

