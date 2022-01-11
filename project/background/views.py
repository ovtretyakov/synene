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

from .models import Task
from .forms import TaskDeleteForm
from .serializers import TaskSerializer



####################################################
#  Task
####################################################
class TaskView(generic.TemplateView):
    template_name = "background/task_list.html"


class TaskAPI(ListAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = "pk"


class TaskDeleteView(BSModalCreateView):
    model = Task
    form_class = TaskDeleteForm
    template_name = 'background/delete_task.html'
    success_message = "Success: Background task was deleted."

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(TaskDeleteView, self).get_context_data(**kwargs)

        pk = self.kwargs['pk']
        if pk:
            object = Task.objects.get(pk=pk)
            context["object"] = object
        return context    

    def get_success_url(self):
        return reverse_lazy("background:task_list")

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                object_id = cleaned_data["object_id"]
                object = Task.objects.get(pk=object_id)
                object.delete()
                messages.success(self.request, self.success_message)
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())
