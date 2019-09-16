from django.conf.urls import url

from . import views

app_name = 'core'
urlpatterns = [
    #Leagues
    url(r'^league/update/(?P<pk>\d+)/$', views.LeagueUpdateView.as_view(), name='update_league'),
]