from django.conf.urls import url

from . import views

app_name = 'betting'
urlpatterns = [
    url(r'^betting/$', views.OddView.as_view(), name='odd_list'),
    url(r'^betting/api/$', views.OddAPI.as_view(), name='odd_list_api'),
]