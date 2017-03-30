from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$',  views.about, name='about'),
    url(r'^home/$',  views.home, name='home'),
    url(r'^create_room/$', views.create_room, name='create_room'),
    url(r'^join_room/$', views.join_room, name='join_room'),
    url(r'^judge_room/$', views.judge_room, name='judge_room'),
    rl(r'^result/$', views.result, name='result'),
    url(r'^(?P<label>[\w-]{,50})/(?P<position>[\w-]{,50})/$', views.chat_room, name='chat_room'),
]
