from django.conf.urls import url

from . import views

app_name = 'load'
urlpatterns = [
    #LoadSource
    url(r'^source$', views.LoadSourcesView.as_view(), name='source_list'),
    url(r'^source/api/$', views.LoadSourcesAPI.as_view(), name='source_list_api'),
    url(r'^source/update/(?P<pk>\d+)/$', views.LoadSourceUpdateView.as_view(), name='update_load_source'),
    url(r'^source/process/(?P<pk>\d+)/$', views.LoadSourceProcessView.as_view(), name='process_load_source'),
    url(r'^source/detail/(?P<pk>\d+)/$', views.LoadSourceDetail.as_view(), name='source_detail'),
    url(r'^source/detail/api/(?P<load_source>\d+)/$', views.LoadSourcesDetailAPI.as_view(), name='source_detail_api'),
    url(r'^source/session/api/(?P<load_source>\d+)/$', views.SourceSessionsAPI.as_view(), name='source_sessions_api'),

    #Errors
    url(r'^errors$', views.ErrorLogView.as_view(), name='errors'),
    url(r'^errors/api/$', views.ErrorLogAPI.as_view(), name='errors_api'),
    url(r'^errors/detail/(?P<pk>\d+)/$', views.ErrorLogDetail.as_view(), name='view_error'),

    #SourceSession
    url(r'^sessions$', views.SourceAllSessionsView.as_view(), name='all_sessions'),
    url(r'^sessions/api/$', views.SourceAllSessionsAPI.as_view(), name='all_sessions_api'),
    url(r'^sessions/detail/(?P<pk>\d+)/$', views.SourceSessionDetail.as_view(), name='view_session'),
]