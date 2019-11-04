from .models import Season


class LeagueGetContextMixin(object):

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)

        leagues = self.get_leagues()
        context["leagues"] = leagues

        date_to = self.request.GET.get("date_to", None)
        if date_to:
            context["date_to"] = date_to
        date_from = self.request.GET.get("date_from", None)
        if date_from:
            context["date_from"] = date_from
        selected_league = self.request.GET.get("selected_league", None)
        if selected_league:
            context["selected_league"] = int(selected_league)

        season_id = self.request.GET.get("season_id", None)
        if season_id:
            selected_season = Season.objects.select_related("league").get(pk=season_id)
            context["selected_league"] = int(selected_season.league.pk)
            context["selected_season"] = selected_season

        return context    
