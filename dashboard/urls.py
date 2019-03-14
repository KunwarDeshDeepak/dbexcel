from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls import url

url_patterns_dashboard = [
    url(r'^$', views.index, name='index'),
    url(r'^zaps/$',views.zaps, name='zaps'),
    url(r'^taskhistory/$',views.taskhistory, name='taskhistory'),
    url(r'^connections/$',views.connections, name='connections'),
    url(r'^config/$',views.config, name='config'),
    url(r'^config/selectsstrigger/$',views.selectsstrigger, name='selectsstrigger'),
    url(r'^config/selectssaccount/$',views.selectssaccount, name='selectssaccount'),
    url(r'^config/setupssissue/$',views.setupssissue, name='setupssissue'),
    url(r'^config/overviewss/$',views.overviewss, name='overviewss'),
    url(r'^config/selectjiratrigger/$',views.selectjiratrigger, name='selectjiratrigger'),
    url(r'^config/selectjiraaccount/$',views.selectjiraaccount, name='selectjiraaccount'),
    url(r'^config/setupjiraissue/$',views.setupjiraissue, name='setupjiraissue'),
    url(r'^config/overview/$',views.overview, name='overview')
]