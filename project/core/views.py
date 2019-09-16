from django.views import generic
from django.http import HttpResponseRedirect

from django.contrib import messages

from rest_framework.generics import ListAPIView
from bootstrap_modal_forms.generic import (BSModalCreateView,
                                           BSModalUpdateView,
                                           BSModalReadView,
                                           BSModalDeleteView)

from .models import League
from .forms import LeagueForm, LeadueMergeForm, LeaguesDeleteForm, LeaguesConfirmForm



####################################################
#  League
####################################################
class LeagueUpdateView(BSModalUpdateView):
    model = League
    template_name = "core/update_league.html"
    form_class = LeagueForm
    success_message = "Success: League was updated."

    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")

    def get_success_message(self):
        return self.success_message

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                self.object.api_update(slug=cleaned_data["slug"], 
                                        name=cleaned_data["name"], 
                                        team_type=cleaned_data["team_type"], 
                                        country=cleaned_data["country"], 
                                        load_status=cleaned_data["load_status"], 
                                        load_source=cleaned_data["load_source"]
                                        )
                messages.success(self.request, self.get_success_message())
            except Exception as e:
                messages.error(self.request, "Updating error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class LeagueMergeView(BSModalUpdateView):
    model = League
    template_name = "core/merge_league.html"
    form_class = LeadueMergeForm
    success_message = "Success: League was merged to %(id)s."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, league_id):
        return self.success_message % {"id":league_id,}

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                league_id = cleaned_data["league_id"]
                self.object.api_merge_to(league_id)
                messages.success(self.request, self.get_success_message(league_id))
            except Exception as e:
                messages.error(self.request, "Merging error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())

class LeaguesDeleteView(generic.TemplateView):
    form_class = LeaguesDeleteForm
    success_message = "Success: %(cnt)s leagues were deleted."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LeaguesDeleteView, self).get_context_data(**kwargs)

        leagues_id = self.request.GET.get("leagues", None)
        if leagues_id:
            context["leagues_id"] = leagues_id

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                leagues_id = cleaned_data["leagues_id"]
                League.api_delete_leagues(leagues_id)
                cnt = len(leagues_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Deleting error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())


class LeaguesConfirmView(BSModalCreateView):
    # model = League
    form_class = LeaguesConfirmForm
    template_name = "football/confirm_leagues.html"
    success_message = "Success: %(cnt)s leagues were confirmed."
    def get_success_url(self):
        return self.request.META.get("HTTP_REFERER")
    def get_success_message(self, cnt):
        return self.success_message % {"cnt":cnt,}

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LeaguesConfirmView, self).get_context_data(**kwargs)

        leagues_id = self.request.GET.get("leagues", None)
        if leagues_id:
            context["leagues_id"] = leagues_id

        return context    

    def form_valid(self, form):
        if self.request.method == "POST" and not self.request.is_ajax():
            try:
                cleaned_data = form.cleaned_data
                leagues_id = cleaned_data["leagues_id"]
                load_source = cleaned_data["load_source"]
                League.api_confirm_leagues(leagues_id, load_source)
                cnt = len(leagues_id.split(","))
                messages.success(self.request, self.get_success_message(cnt))
            except Exception as e:
                messages.error(self.request, "Confirming error :\n" + str(e))
        return HttpResponseRedirect(self.get_success_url())



