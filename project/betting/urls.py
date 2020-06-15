from django.conf.urls import url

from . import views

app_name = 'betting'
urlpatterns = [
    url(r'^odds/$', views.OddView.as_view(), name='odd_list'),
    url(r'^odds/api/$', views.OddAPI.as_view(), name='odd_list_api'),
    url(r'^odds/detail/(?P<pk>\d+)/$', views.OddDetail.as_view(), name='odd_detail'),
]