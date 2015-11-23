# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

import views.auth
import views.main

urlpatterns = [
    # Админка
    url(r'^admin/', include(admin.site.urls)),

    # Общие
    url(r'^poll/(?P<pk>\d+)/$', views.main.PollDetailView.as_view(),
        name='poll_details'),
    url(r'^poll/try/(?P<slug>[\w-]+)/$', views.main.TryPoll.as_view(),
        name='try_poll'),
    url(r'^$', views.main.PollListView.as_view(), name='index'),

    # Ответы
    url(r'^my_polls/poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/'
        r'(?P<pk>\d+)/delete/',
        views.main.AnswerDeleteView.as_view(), name='answer_delete'),
    url(r'^my_polls/poll/(?P<poll_pk>\d+)/'
        r'question/(?P<top_object_pk>\d+)/answer/(?P<pk>\d+)/edit/',
        views.main.AnswerUpdateView.as_view(), name='answer_edit'),
    url(r'^my_polls/poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/add/',
        views.main.AnswerCreateView.as_view(), name='answer_add'),

    # Вопросы
    url(r'^my_polls/poll/(?P<top_object_pk>\d+)/question/(?P<pk>\d+)/delete/',
        views.main.QuestionDeleteView.as_view(), name='question_delete'),
    url(r'^my_polls/poll/(?P<top_object_pk>\d+)/question/(?P<pk>\d+)/edit/',
        views.main.QuestionUpdateView.as_view(), name='question_edit'),
    url(r'^my_polls/poll/(?P<top_object_pk>\d+)/question/add/',
        views.main.QuestionCreateView.as_view(), name='question_add'),


    # Опросы
    url(r'^my_polls/poll/(?P<pk>\d+)/delete/',
        views.main.PollDeleteView.as_view(), name='user_poll_delete'),
    url(r'^my_polls/poll/(?P<pk>\d+)/edit/',
        views.main.PollUpdateView.as_view(), name='user_poll_edit'),
    url(r'^my_polls/poll/add/', views.main.PollCreateView.as_view(),
        name='user_poll_add'),
    url(r'^my_polls/poll/(?P<pk>\d+)/$',
        views.main.UserPollDetailView.as_view(), name='user_poll_details'),
    url(r'^my_polls/', views.main.UserPollListView.as_view(),
        name='user_polls'),


    # Авторизация
    url(r'^registration/login/$', 'django.contrib.auth.views.login'),
    url(r'^registration/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^registration/register/$', views.auth.register, name='register'),
]
