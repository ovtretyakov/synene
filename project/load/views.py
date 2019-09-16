import datetime

from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from project.core.utils import get_date_from_string
from project.core.models import LoadSource
from .models import ErrorLog, SourceDetail, SourceSession
from .serializers import   (LoadSourceSerializer, 
                            SourceDetailSerializer, 
                            ErrorLogSerializer, 
                            SourceSessionsSerializer,
                            SourceAllSessionsSerializer,
                            )
from .forms import LoadSourceForm, LoadSourceProcessForm


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

    # def get_queryset(self):
    #   queryset = LoadSource.objects.all()

    #   # author_name = self.request.query_params.get("author_name", None)
    #   # if author_name:
    #   #     queryset = queryset.filter(Q(first_name__icontains=author_name) | Q(last_name__icontains=author_name))
    #   # date_from = get_date_from_string(self.request.query_params.get("date_from", None))
    #   # if date_from:
    #   #     queryset = queryset.filter(date_of_birth__gte=date_from)
    #   # date_to = get_date_from_string(self.request.query_params.get("date_to", None))
    #   # if date_to:
    #   #     queryset = queryset.filter(date_of_birth__lte=date_to)
    #   return queryset

class LoadSourceUpdateView(BSModalUpdateView):
    model = LoadSource
    template_name = "load/update_load_source.html"
    form_class = LoadSourceForm
    success_message = "Success: Load sources was updated."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

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
            try:
                self.object.download()
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Processing error :\n" + str(e))
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


