# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

import views.auth
import views.main
import views.stat

urlpatterns = [
    # Админка
    url(r'^admin/', include(admin.site.urls)),

    # Общие
    url(r'^poll/(?P<pk>\d+)/finish/$', views.main.PollFinishView.as_view(),
        name='finish_poll'),
    url(r'^poll/(?P<pk>\d+)/$', views.main.PollDetailView.as_view(),
        name='poll_details'),
    url(r'^poll/(?P<slug>[\w-]+)/try/$', views.main.PollTryView.as_view(),
        name='try_poll'),
    url(r'^$', views.main.PollListView.as_view(), name='index'),

    # Ответы
    url(r'^(?P<username>\w+)/poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/'
        r'(?P<pk>\d+)/delete/',
        views.main.AnswerDeleteView.as_view(), name='answer_delete'),
    url(r'^(?P<username>\w+)/poll/(?P<poll_pk>\d+)/'
        r'question/(?P<top_object_pk>\d+)/answer/(?P<pk>\d+)/edit/',
        views.main.AnswerUpdateView.as_view(), name='answer_edit'),
    url(r'^(?P<username>\w+)/poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/add/',
        views.main.AnswerCreateView.as_view(), name='answer_add'),

    # Вопросы
    url(r'^(?P<username>\w+)/poll/(?P<top_object_pk>\d+)/'
        r'question/(?P<pk>\d+)/delete/',
        views.main.QuestionDeleteView.as_view(), name='question_delete'),
    url(r'^(?P<username>\w+)/poll/(?P<top_object_pk>\d+)/'
        r'question/(?P<pk>\d+)/edit/',
        views.main.QuestionUpdateView.as_view(), name='question_edit'),
    url(r'^(?P<username>\w+)/poll/(?P<top_object_pk>\d+)/question/add/',
        views.main.QuestionCreateView.as_view(), name='question_add'),


    # Опросы
    url(r'^(?P<username>\w+)/poll/(?P<pk>\d+)/delete/',
        views.main.PollDeleteView.as_view(), name='user_poll_delete'),
    url(r'^(?P<username>\w+)/poll/(?P<pk>\d+)/edit/',
        views.main.PollUpdateView.as_view(), name='user_poll_edit'),
    url(r'^(?P<username>\w+)/poll/add/', views.main.PollCreateView.as_view(),
        name='user_poll_add'),
    url(r'^(?P<username>\w+)/poll/(?P<pk>\d+)/$',
        views.main.UserPollDetailView.as_view(), name='user_poll_details'),
    url(r'^(?P<username>\w+)/polls/', views.main.UserPollListView.as_view(),
        name='user_polls'),

    # Статистика
    url(r'^(?P<username>\w+)/statistics/polls/',
        views.stat.PollsPopularView.as_view(), name='user_poll_stat'),
    url(r'^(?P<username>\w+)/statistics/questions/',
        views.stat.QuestionsPopularView.as_view(), name='user_questions_stat'),


    # Авторизация
    url(r'^registration/login/$', 'django.contrib.auth.views.login'),
    url(r'^registration/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^registration/register/$', views.auth.register, name='registration'),
]
