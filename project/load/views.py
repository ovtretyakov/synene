import datetime

from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)
from background_task import background

from project.core.utils import get_date_from_string
from project.core.models import LoadSource
from .models import ErrorLog, SourceDetail, SourceSession
from .serializers import   (LoadSourceSerializer, 
                            SourceDetailSerializer, 
                            ErrorLogSerializer, 
                            SourceSessionsSerializer,
                            SourceAllSessionsSerializer,
                            )
from .forms import LoadSourceForm, LoadSourceProcessForm, LoadSourceProcessAllForm

from project.core.views import (LeagueMergeView, LeaguesDeleteView, LeaguesConfirmView,
                                SeasonAPI,
                                MatchAPI,
                                TeamMergeView, TeamsDeleteView, TeamsConfirmView,
                                RefereeMergeView, RefereesDeleteView, RefereesConfirmView,
                                )


@background
def load_source_download(load_source_pk, local_files):
    load_source = LoadSource.objects.get(pk=load_source_pk)
    load_source.download(local_files)


####################################################
#  LoadSource
####################################################
class LoadSourcesView(generic.TemplateView):
    template_name = "load/source_list.html"

    # def get_context_data(self, **kwargs):

    #     # Call the base implementation first to get the context
    #     context = super(BootstrapIndex, self).get_context_data(**kwargs)
    #     # Filter data
    #     author_name = self.request.GET.get("author_name", None)
    #     if author_name:
    #         context["author_name"] = author_name
    #     date_to = self.request.GET.get("date_to", None)
    #     if date_to and get_date_from_string(date_to):
    #         context["date_to"] = date_to
    #     date_from_str = self.request.GET.get("date_from", None)
    #     date_from = get_date_from_string(date_from_str)
    #     if date_from_str and date_from:
    #         context["date_from"] = date_from_str
    #     return context    


class LoadSourcesAPI(ListAPIView):
    serializer_class = LoadSourceSerializer
    queryset = LoadSource.objects.order_by("pk")
    lookup_field = "pk"

    def get_queryset(self):
      queryset = LoadSource.objects.all()

      loadable = self.request.query_params.get("loadable", None)
      if loadable and loadable:
          queryset = queryset.filter(is_loadable=True)
      # date_from = get_date_from_string(self.request.query_params.get("date_from", None))
      # if date_from:
      #     queryset = queryset.filter(date_of_birth__gte=date_from)
      # date_to = get_date_from_string(self.request.query_params.get("date_to", None))
      # if date_to:
      #     queryset = queryset.filter(date_of_birth__lte=date_to)
      return queryset

class LoadSourceUpdateView(BSModalUpdateView):
    model = LoadSource
    template_name = "load/update_load_source.html"
    form_class = LoadSourceForm
    success_message = "Success: Load sources was updated."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def form_valid(self, form):

        if self.request.method == "POST" and not self.request.is_ajax():
            cleaned_data = form.cleaned_data
            new_load_date = cleaned_data["load_date"] 
            if new_load_date:
                (SourceDetail.objects.filter(load_source=self.object)
                                    .filter(load_date__isnull=False)
                                    .filter(load_date__gt=new_load_date)
                                    .update(load_date=new_load_date)
                )
        return super().form_valid(form)

class LoadSourceProcessView(BSModalUpdateView):
    model = LoadSource
    template_name = "load/process_load_source.html"
    form_class = LoadSourceProcessForm
    success_message = 'Downloading "%(name)s"  is queued for processing'
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self):
        return self.success_message % {"name":self.object.name,}

    def form_valid(self, form):
        # self.object = form.save()
        # do something with self.object
        # remember the import: from django.http import HttpResponseRedirect

        if self.request.method == "POST" and not self.request.is_ajax():
            cleaned_data = form.cleaned_data
            try:
                load_source_download(self.object.pk, cleaned_data["local_files"])
                # self.object.download()
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Processing error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class LoadSourceProcessAllView(BSModalCreateView):
    form_class = LoadSourceProcessAllForm
    template_name = "load/source_process_all.html"
    success_message = "Success: %(cnt)s sources were queued for processing."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LoadSourceProcessAllView, self).get_context_data(**kwargs)

        # leagues_id = self.request.GET.get("leagues", None)
        # if leagues_id:
        #     context["leagues_id"] = leagues_id

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
            #     cleaned_data = form.cleaned_data
            #     leagues_id = cleaned_data["leagues_id"]
            #     League.api_delete_leagues(leagues_id)
            #     cnt = len(leagues_id.split(","))

                cnt = 0
                for load_source in LoadSource.objects.filter(is_loadable=True).order_by("reliability"):
                    load_source_download(load_source.pk, False)
                    cnt += 1

                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Error:\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


####################################################
#  SourceDetail
####################################################
class LoadSourceDetail(BSModalReadView):
    model = LoadSource
    template_name = 'load/source_detail.html'


class LoadSourcesDetailAPI(ListAPIView):
    serializer_class = SourceDetailSerializer
    # queryset = SourceDetail.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        load_source = self.kwargs.get("load_source",0)
        queryset = SourceDetail.objects.all()
        if load_source:
            queryset = queryset.filter(load_source=load_source)
        return queryset

####################################################
#  SourceSession
####################################################
class SourceAllSessionsView(generic.TemplateView):
    template_name = "load/session_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(SourceAllSessionsView, self).get_context_data(**kwargs)
        load_sources = LoadSource.objects.all().order_by("pk")
        context["sources"] = load_sources

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_source = self.request.GET.get("source", None)
        if selected_source:
            context["selected_source"] = int(selected_source)

        return context    


class SourceSessionsAPI(ListAPIView):
    serializer_class = SourceSessionsSerializer
    # queryset = SourceDetail.objects.all()
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        load_source = self.kwargs.get("load_source",0)
        queryset = SourceSession.objects.all()
        if load_source:
            queryset = queryset.filter(load_source=load_source)
        return queryset


class SourceAllSessionsAPI(ListAPIView):
    serializer_class = SourceAllSessionsSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = SourceSession.objects.all()
        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(start_time__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(start_time__lte=date_to)
        load_source_id = self.request.query_params.get("selected_source", None)
        if load_source_id and int(load_source_id) > 0:
            queryset = queryset.filter(load_source=load_source_id)

        return queryset

class SourceSessionDetail(BSModalReadView):
    model = SourceSession
    template_name = 'load/source_session_detail.html'



####################################################
#  Errors
####################################################
class ErrorLogView(generic.TemplateView):
    template_name = "load/error_list.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ErrorLogView, self).get_context_data(**kwargs)
        load_sources = LoadSource.objects.all().order_by("pk")
        context["sources"] = load_sources

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_source = self.request.GET.get("source", None)
        if selected_source:
            context["selected_source"] = int(selected_source)

        return context    


class ErrorLogAPI(ListAPIView):
    serializer_class = ErrorLogSerializer
    lookup_field = "pk"

    def get_queryset(self, *args, **kwargs):
        queryset = ErrorLog.objects.all()

        date_from = get_date_from_string(self.request.query_params.get("date_from", None))
        if date_from:
            queryset = queryset.filter(error_time__gte=date_from)
        date_to = get_date_from_string(self.request.query_params.get("date_to", None))
        if date_to:
            queryset = queryset.filter(error_time__lte=date_to)
        load_source_id = self.request.query_params.get("selected_source", None)
        if load_source_id and int(load_source_id) > 0:
            queryset = queryset.filter(load_source=load_source_id)
        source_session_id = self.request.query_params.get("source_session", None)
        if source_session_id:
            queryset = queryset.filter(source_session=source_session_id)

        return queryset


class ErrorLogDetail(BSModalReadView):
    model = ErrorLog
    template_name = 'load/error_log_detail.html'


