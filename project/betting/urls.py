from django.conf.urls import url

from . import views

app_name = 'betting'
urlpatterns = [
    url(r'^odds/$', views.OddView.as_view(), name='odd_list'),
    url(r'^odds/api/$', views.OddAPI.as_view(), name='odd_list_api'),
    url(r'^odds/detail/(?P<pk>\d+)/$', views.OddDetail.as_view(), name='odd_detail'),
    #harvest handler
    url(r'^odds/harvest/handler/$', views.HarvestHandlerView.as_view(), name='harvest_handler_list'),
    url(r'^odds/harvest/handler/api/$', views.HarvestHandlerAPI.as_view(), name='harvest_handler_list_api'),
    url(r'^odds/harvest/handler/create/$', views.HarvestHandlerCreateView.as_view(), name='create_harvest_handler'),
    url(r'^odds/harvest/handler/update/(?P<pk>\d+)/$', views.HarvestHandlerUpdateView.as_view(), name='update_harvest_handler'),
    url(r'^odds/harvest/handler/delete/(?P<pk>\d+)/$', views.HarvestHandlerDeleteView.as_view(), name='delete_harvest_handler'),
    #harvest
    url(r'^odds/harvest/$', views.HarvestView.as_view(), name='harvest_list'),
    url(r'^odds/harvest/api/$', views.HarvestAPI.as_view(), name='harvest_list_api'),
    url(r'^odds/harvest/create/$', views.HarvestCreateView.as_view(), name='create_harvest'),
    url(r'^odds/harvest/update/(?P<pk>\d+)/$', views.HarvestUpdateView.as_view(), name='update_harvest'),
    url(r'^odds/harvest/delete/(?P<pk>\d+)/$', views.HarvestDeleteView.as_view(), name='delete_harvest'),
    url(r'^odds/harvest/harvest/(?P<pk>\d+)/$', views.HarvestDoHarvestView.as_view(), name='do_harvest_harvest'),
    url(r'^odds/harvest/harvest/$', views.HarvestDoHarvestAllView.as_view(), name='do_harvest_harvest_all'),
    #harvest config
    url(r'^odds/harvest/config/(?P<harvest>\d+)/api/$', views.HarvestConfigAPI.as_view(), name='harvest_config_api'),
    url(r'^odds/harvest/config/(?P<harvest>\d+)/create/$', views.HarvestConfigCreateView.as_view(), name='create_harvest_config'),
    url(r'^odds/harvest/config/delete/(?P<pk>\d+)/$', views.HarvestConfigDeleteView.as_view(), name='delete_harvest_config'),
    #harvest group
    url(r'^odds/harvest/group/(?P<harvest>\d+)/api/$', views.HarvestGroupAPI.as_view(), name='harvest_group_api'),
    url(r'^odds/harvest/group/(?P<harvest>\d+)/create/$', views.HarvestGroupCreateView.as_view(), name='create_harvest_group'),
    url(r'^odds/harvest/group/update/(?P<pk>\d+)/$', views.HarvestGroupUpdateView.as_view(), name='update_harvest_group'),
    url(r'^odds/harvest/group/delete/(?P<pk>\d+)/$', views.HarvestGroupDeleteView.as_view(), name='delete_harvest_group'),
    url(r'^odds/harvest/group/harvest/(?P<pk>\d+)/$', views.HarvestGroupDoHarvestView.as_view(), name='do_harvest_harvest_group'),
    #harvest league
    url(r'^odds/harvest/league/(?P<harvest_group>\d+)/create/$', views.HarvestLeagueCreateView.as_view(), name='create_harvest_league'),
    url(r'^odds/harvest/league/delete/(?P<pk>\d+)/$', views.HarvestLeagueDeleteView.as_view(), name='delete_harvest_league'),
    ####
]