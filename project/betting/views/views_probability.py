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
from ..models import Distribution
from ..forms import DistributionForm, DistributionGatherForm, DistributionDeleteForm
from ..serializers import DistributionSerializer


@background
def distribution_gather(distribution_pk, start_date_str, end_date_str):
    start_date = get_date_from_string(start_date_str)
    end_date = get_date_from_string(end_date_str)
    distribution = Distribution.objects.get(pk=distribution_pk)
    distribution.api_gathering(start_date=start_date, end_date=end_date)



####################################################
#  Distribution
####################################################
class DistributionView(generic.TemplateView):
    template_name = "betting/distribution_list.html"


class DistributionAPI(ListAPIView):
    serializer_class = DistributionSerializer
    queryset = Distribution.objects.all()
    lookup_field = "pk"


class DistributionCreateView(BSModalCreateView):
    model = Distribution
    form_class = DistributionForm
    template_name = 'betting/create_distribution.html'
    success_message = "Success: Distibution was created."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class DistributionUpdateView(BSModalUpdateView):
    model = Distribution
    form_class = DistributionForm
    template_name = 'betting/update_distribution.html'
    success_message = "Success: Distibution was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")


class DistributionGatheringView(BSModalUpdateView):
    model = Distribution
    form_class = DistributionGatherForm
    template_name = 'betting/gather_distribution.html'
    success_message = "Success: Distribution was prepared for gathering."

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
                end_date = cleaned_data["end_date"]
                end_date_str = ""
                if end_date:
                    end_date_str = end_date.strftime('%d.%m.%Y')

                distribution_gather(self.object.pk, start_date_str, end_date_str)    
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class DistributionDeleteView(BSModalCreateView):
    model = Distribution
    form_class = DistributionDeleteForm
    template_name = 'betting/delete_distribution.html'
    success_message = "Success: Distribution was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(DistributionDeleteView, self).get_context_data(**kwargs)

        # pk = self.request.GET.get("pk", None)
        pk = self.kwargs['pk']
        if pk:
            object = Distribution.objects.get(pk=pk)
            context["object"] = object

        return context    

    def get_success_url(self):
        return reverse_lazy("betting:distribution_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = Distribution.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())
