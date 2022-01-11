from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.query import RawQuerySet
from django.db.models import sql

from background_task import background

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string
from project.core.models import Sport
from ..models import (HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague,
                     ForecastHandler, Predictor, ForecastSet)
from ..forms import (HarvestHandlerForm, HarvestHandlerDeleteForm,
                     HarvestForm, HarvestDeleteForm, HarvestDoHarvestForm, HarvestDoHarvestAllForm,
                     HarvestConfigForm, HarvestConfigDeleteForm,
                     HarvestGroupForm, HarvestGroupDeleteForm, HarvestGroupDoHarvestForm,
                     HarvestLeagueForm, HarvestLeagueDeleteForm,
                     ForecastHandlerForm, ForecastHandlerDeleteForm,
                     PredictorForm, PredictorDeleteForm,
                     ForecastSetForm, ForecastSetDeleteForm
                     )
from ..serializers import (HarvestHandlerSerializer, HarvestSerializer, HarvestConfigSerializer, HarvestGroupSerializer,
                           ForecastHandlerSerializer, PredictorSerializer, ForecastSetSerializer
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
