from django.conf.urls import url

from . import views

app_name = 'football'
urlpatterns = [
    #FootballLeagues
    url(r'^leagues/$', views.FootballLeagueView.as_view(), name='league_list'),
    url(r'^league_select/$', views.SelectFootballLeagueView.as_view(), name='select_league'),
    url(r'^leagues/api/$', views.FootballLeagueAPI.as_view(), name='league_list_api'),
    url(r'^league/merge/(?P<pk>\d+)/$', views.FootballLeagueMergeView.as_view(), name='merge_league'),
    url(r'^leagues/delete/$', views.FootballLeaguesDeleteView.as_view(), name='delete_leagues'),
    url(r'^leagues/confirm/$', views.FootballLeaguesConfirmView.as_view(), name='confirm_leagues'),
    #FootballSeasons
    url(r'^seasons/$', views.FootballSeasonView.as_view(), name='season_list'),
    url(r'^seasons/api/$', views.FootballSeasonAPI.as_view(), name='season_list_api'),
    #FootballMatches
    url(r'^matches/$', views.FootballMatchView.as_view(), name='match_list'),
    url(r'^matches/api/$', views.FootballMatchAPI.as_view(), name='match_list_api'),
]