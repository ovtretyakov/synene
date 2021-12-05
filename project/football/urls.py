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
    #FootballTeams
    url(r'^teams/$', views.FootballTeamView.as_view(), name='team_list'),
    url(r'^team_select/$', views.SelectFootballTeamView.as_view(), name='select_team'),
    url(r'^teams/api/$', views.FootballTeamAPI.as_view(), name='team_list_api'),
    url(r'^team/merge/(?P<pk>\d+)/$', views.FootballTeamMergeView.as_view(), name='merge_team'),
    url(r'^teams/delete/$', views.FootballTeamsDeleteView.as_view(), name='delete_teams'),
    url(r'^teams/confirm/$', views.FootballTeamsConfirmView.as_view(), name='confirm_teams'),
    #FootballReferees
    url(r'^referees/$', views.FootballRefereeView.as_view(), name='referee_list'),
    url(r'^referee_select/$', views.SelectFootballRefereeView.as_view(), name='select_referee'),
    url(r'^referees/api/$', views.FootballRefereeAPI.as_view(), name='referee_list_api'),
    url(r'^referee/merge/(?P<pk>\d+)/$', views.FootballRefereeMergeView.as_view(), name='merge_referee'),
    url(r'^referees/delete/$', views.FootballRefereesDeleteView.as_view(), name='delete_referees'),
    url(r'^referees/confirm/$', views.FootballRefereesConfirmView.as_view(), name='confirm_referees'),
]