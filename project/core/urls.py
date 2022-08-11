from django.conf.urls import url

from . import views

app_name = 'core'
urlpatterns = [
    #Leagues
    url(r'^league/update/(?P<pk>\d+)/$', views.LeagueUpdateView.as_view(), name='update_league'),
    #Matches
    url(r'^match/detail/(?P<pk>\d+)/$', views.MatchDetailView.as_view(), name='match_detail'),
    url(r'^match/stats/api/$', views.MatchStatsAPI.as_view(), name='match_stats_api'),
    #Team
    url(r'^team/update/(?P<pk>\d+)/$', views.TeamUpdateView.as_view(), name='update_team'),
    #Team
    url(r'^referee/update/(?P<pk>\d+)/$', views.RefereeUpdateView.as_view(), name='update_referee'),
    # Season`
    url(r'^season/create/$', views.SeasonCreateView.as_view(), name='create_season'),
    url(r'^season/update/(?P<pk>\d+)/$', views.SeasonUpdateView.as_view(), name='update_season'),
]