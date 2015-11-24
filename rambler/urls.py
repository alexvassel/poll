# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

import views.auth
import views.main
import views.admin

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

    url(r'^$', views.main.PollListView.as_view(anonymous=True), name='index'),

    # Ответы
    url(r'^poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/'
        r'(?P<pk>\d+)/delete/',
        views.main.AnswerDeleteView.as_view(), name='answer_delete'),
    url(r'^poll/(?P<poll_pk>\d+)/'
        r'question/(?P<top_object_pk>\d+)/answer/(?P<pk>\d+)/edit/',
        views.main.AnswerUpdateView.as_view(), name='answer_edit'),
    url(r'^poll/(?P<poll_pk>\d+)/question/'
        r'(?P<top_object_pk>\d+)/answer/add/',
        views.main.AnswerCreateView.as_view(), name='answer_add'),

    # Вопросы
    url(r'^poll/(?P<top_object_pk>\d+)/'
        r'question/(?P<pk>\d+)/delete/',
        views.main.QuestionDeleteView.as_view(), name='question_delete'),
    url(r'^poll/(?P<top_object_pk>\d+)/'
        r'question/(?P<pk>\d+)/edit/',
        views.main.QuestionUpdateView.as_view(), name='question_edit'),
    url(r'^poll/(?P<top_object_pk>\d+)/question/add/',
        views.main.QuestionCreateView.as_view(), name='question_add'),


    # Опросы
    url(r'poll/(?P<pk>\d+)/delete/',
        views.main.PollDeleteView.as_view(), name='user_poll_delete'),
    url(r'^poll/(?P<pk>\d+)/edit/',
        views.main.PollUpdateView.as_view(), name='user_poll_edit'),
    url(r'^poll/add/', views.main.PollCreateView.as_view(),
        name='user_poll_add'),
    url(r'^poll/(?P<pk>\d+)/$',
        views.main.PollDetailView.as_view(), name='user_poll_details'),
    url(r'^polls/', views.main.PollListView.as_view(),
        name='user_polls'),

    # Статистика
    url(r'^statistics/polls/',
        views.main.UserStat.as_view(), name='user_stat'),


    # Авторизация
    url(r'^registration/login/$', 'django.contrib.auth.views.login'),
    url(r'^registration/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    url(r'^registration/register/$', views.auth.register, name='registration'),

    # Админитратор
    url(r'^administrator/user/(?P<pk>\d+)/edit/',
        views.admin.UserDetailView.as_view(), name='admin_user'),
    url(r'^administrator/stat/', views.admin.StatView.as_view(),
        name='admin_stat'),
    url(r'^administrator/users/', views.admin.UsersView.as_view(),
        name='admin_users'),
]
