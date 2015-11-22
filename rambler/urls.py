# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

import views.auth
import views.main

urlpatterns = [
    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # App
    url(r'^poll/(?P<slug>[\w-]+)/$', views.main.PollDetailView.as_view(),
        name='poll_details'),
    url(r'^$', views.main.PollListView.as_view(), name='index'),
    url(r'^poll/try/(?P<slug>[\w-]+)/$', views.main.TryPoll.as_view(),

    # Auth
    url(r'^registration/login/$', 'django.contrib.auth.views.login'),
    url(r'^registration/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^registration/register/$', views.auth.register, name='register'),

]
