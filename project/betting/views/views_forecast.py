from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models.query import RawQuerySet
from django.db.models import sql


from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string
from project.core.models import Sport
from ..models import HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague
from ..forms import (HarvestHandlerForm, HarvestHandlerDeleteForm,
                     HarvestForm, HarvestDeleteForm,
                     HarvestConfigForm, HarvestConfigDeleteForm,
                     HarvestGroupForm, HarvestGroupDeleteForm,
                     HarvestLeagueForm, HarvestLeagueDeleteForm,
                     )
from ..serializers import HarvestHandlerSerializer, HarvestSerializer, HarvestConfigSerializer, HarvestGroupSerializer



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
