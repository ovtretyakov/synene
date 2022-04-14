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
    url(r'^odds/harvest/copy/(?P<pk>\d+)/$', views.HarvestCopyView.as_view(), name='copy_harvest'),
    url(r'^odds/harvest/adjust/(?P<pk>\d+)/$', views.HarvestAdjustView.as_view(), name='adjust_harvest'),
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
    #forecast handler
    url(r'^odds/forecast/handler/$', views.ForecastHandlerView.as_view(), name='forecast_handler_list'),
    url(r'^odds/forecast/handler/api/$', views.ForecastHandlerAPI.as_view(), name='forecast_handler_list_api'),
    url(r'^odds/forecast/handler/create/$', views.ForecastHandlerCreateView.as_view(), name='create_forecast_handler'),
    url(r'^odds/forecast/handler/update/(?P<pk>\d+)/$', views.ForecastHandlerUpdateView.as_view(), name='update_forecast_handler'),
    url(r'^odds/forecast/handler/delete/(?P<pk>\d+)/$', views.ForecastHandlerDeleteView.as_view(), name='delete_forecast_handler'),
    #predictor
    url(r'^odds/forecast/predictor/$', views.PredictorView.as_view(), name='predictor_list'),
    url(r'^odds/forecast/predictor/api/$', views.PredictorAPI.as_view(), name='predictor_list_api'),
    url(r'^odds/forecast/predictor/create/$', views.PredictorCreateView.as_view(), name='create_predictor'),
    url(r'^odds/forecast/predictor/update/(?P<pk>\d+)/$', views.PredictorUpdateView.as_view(), name='update_predictor'),
    url(r'^odds/forecast/predictor/delete/(?P<pk>\d+)/$', views.PredictorDeleteView.as_view(), name='delete_predictor'),
    #forecast set
    url(r'^odds/forecast/set/$', views.ForecastSetView.as_view(), name='forecast_set_list'),
    url(r'^odds/forecast/set/api/$', views.ForecastSetAPI.as_view(), name='forecast_set_list_api'),
    url(r'^odds/forecast/set/create/$', views.ForecastSetCreateView.as_view(), name='create_forecast_set'),
    url(r'^odds/forecast/set/update/(?P<pk>\d+)/$', views.ForecastSetUpdateView.as_view(), name='update_forecast_set'),
    url(r'^odds/forecast/set/delete/(?P<pk>\d+)/$', views.ForecastSetDeleteView.as_view(), name='delete_forecast_set'),
    #distribution
    url(r'^odds/distribution/$', views.DistributionView.as_view(), name='distribution_list'),
    url(r'^odds/distribution/api/$', views.DistributionAPI.as_view(), name='distribution_list_api'),
    url(r'^odds/distribution/create/$', views.DistributionCreateView.as_view(), name='create_distribution'),
    url(r'^odds/distribution/update/(?P<pk>\d+)/$', views.DistributionUpdateView.as_view(), name='update_distribution'),
    url(r'^odds/distribution/delete/(?P<pk>\d+)/$', views.DistributionDeleteView.as_view(), name='delete_distribution'),
    url(r'^odds/distribution/gather/(?P<pk>\d+)/$', views.DistributionGatheringView.as_view(), name='gather_distribution'),
    #forecast matches
    url(r'^odds/forecast/set/matches/(?P<forecast_set>\d+)/$', views.ForecastMatchesView.as_view(), name='forecast_match_list'),
    url(r'^odds/forecast/set/matches/(?P<forecast_set>\d+)/api/$', views.ForecastMatchesAPI.as_view(), name='forecast_match_list_api'),
    url(r'^odds/forecast/set/(?P<forecast_set>\d+)/(?P<pk>\d+)/$', views.ForecastMatchDetail.as_view(), name='forecast_match_detail'),
    url(r'^odds/forecast/previous/matches/(?P<match>\d+)/(?P<team>[ah]+)/api/$', views.PreviousMatchesAPI.as_view(), name='previous_matches_api'),
    url(r'^odds/season/chart/(?P<match>\d+)/api/$', views.SeasonChartAPI.as_view(), name='season_chart_api'),
    url(r'^odds/forecast/match/update/(?P<forecast_set>\d+)/(?P<pk>\d+)/$', views.MatchXGUpdateView.as_view(), name='forecast_match_xg_update'),
    url(r'^odds/forecast/match/restore/(?P<forecast_set>\d+)/(?P<pk>\d+)/$', views.MatchXGRestoreView.as_view(), name='forecast_match_xg_restore'),
    #forecast
    url(r'^odds/forecast/(?P<forecast_set>\d+)/(?P<match>\d+)/$', views.ForecastAPI.as_view(), name='forecast_odd_api'),
    #bet type
    url(r'^odds/bet_type/select/$', views.SelectBetTypeView.as_view(), name='select_bet_type'),
    url(r'^odds/bet_type/api/$', views.BetTypeAPI.as_view(), name='bet_type_api'),
    #process all
    url(r'^odds/process/all/$', views.ProccessAllView.as_view(), name='process_all'),
    #select all
    url(r'^odds/pick/$', views.PickOddsView.as_view(), name='pick_odds'),
    url(r'^odds/deselect/(?P<pk>\d+)/$', views.DeselectOddView.as_view(), name='deselect_odd'),
    #selected odd
    url(r'^odds/selected/$', views.SelectedOddsView.as_view(), name='selected_odd_list'),
    url(r'^odds/selected/api/$', views.SelectedOddListAPI.as_view(), name='selected_odd_list_api'),
    url(r'^odds/selected/delete/$', views.SelectedOddsDeleteView.as_view(), name='delete_selected_odds'),
    url(r'^odds/selected/hide/$', views.SelectedOddsHideView.as_view(), name='hide_selected_odds'),
    #Bet
    url(r'^odds/bet/$', views.MyBetView.as_view(), name='my_bet_list'),
    url(r'^odds/bet/api/$', views.MyBetAPI.as_view(), name='my_bet_api'),
    url(r'^odds/bet/create/$', views.CreateBetView.as_view(), name='create_bet'),
    url(r'^odds/bet/detail/(?P<pk>\d+)/$', views.MyBetDetail.as_view(), name='my_bet_detail'),
    url(r'^odds/bet/odd/(?P<pk>\d+)/$', views.BetOddAPI.as_view(), name='bet_odd_api'),
    url(r'^odds/bet/delete/(?P<pk>\d+)/$', views.MyBetDelete.as_view(), name='my_bet_delete'),
    #Transaction
    url(r'^odds/transaction/$', views.TransactionView.as_view(), name='transaction_list'),
    url(r'^odds/transaction/api/$', views.TransactionAPI.as_view(), name='transaction_api'),
    url(r'^odds/transaction/create/$', views.TransactionCreateView.as_view(), name='create_transaction'),
    url(r'^odds/transaction/delete/(?P<pk>\d+)/$', views.TransactionDeleteView.as_view(), name='delete_transaction'),
    ####
]