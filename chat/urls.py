from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$',  views.about, name='about'),
    url(r'^home/$',  views.about, name='about'),
    url(r'^create_room/$', views.create_room, name='create_room'),
    url(r'^join_room/$', views.join_room, name='join_room'),
    url(r'^(?P<label>[\w-]{,50})/$', views.chat_room, name='chat_room'),
]
