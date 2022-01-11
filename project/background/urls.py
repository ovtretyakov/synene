from django.conf.urls import url

from . import views

app_name = 'background'
urlpatterns = [
    url(r'^odds/background/task/$', views.TaskView.as_view(), name='task_list'),
    url(r'^odds/background/task/api/$', views.TaskAPI.as_view(), name='task_list_api'),
    url(r'^odds/background/task/delete/(?P<pk>\d+)/$', views.TaskDeleteView.as_view(), name='delete_task'),
]