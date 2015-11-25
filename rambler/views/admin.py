# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView, ListView, UpdateView
from rambler.models import Poll, PollUser, Question, UserAnswer


class StatView(TemplateView):
    """Статистика, видная админу"""
    template_name = 'rambler/administrator/common_stat.html'

    def get_context_data(self, **kwargs):
        context = super(StatView, self).get_context_data(**kwargs)

        all_polls = Poll.objects.count()
        all_users = PollUser.objects.count()
        all_answers = UserAnswer.objects.count()

        # "Администратор видит сводную информацию
        # по общему кол-ву пользователей, опросам и ответам"
        context['all_polls'] = all_polls
        context['all_users'] = all_users
        context['all_questions'] = Question.objects.count()
        context['all_answers'] = all_answers

        # Администратор видит информацию о:
        #  среднем опросов приходится на пользователя
        #  среднем ответов приходится на пользователя
        #  среднем ответов приходиться на опрос
        context['average_poll_user'] = (float(all_polls) /
                                        all_users) if all_users else 0
        context['average_answers_user'] = (float(all_answers) /
                                           all_users) if all_users else 0
        context['average_answers_poll'] = (float(all_answers) /
                                           all_polls) if all_polls else 0
        context['popular_users'] = (PollUser.objects.annotate(
                                    cnt=Count('finished_polls')))
        return context


class PopularPollsView(ListView):
    template_name = 'rambler/administrator/popular_polls_list.html'
    context_object_name = 'instances'

    POLLS_PER_PAGE = 1

    # "Администратор видит статистику
    # по самым популярным пользователям и опросам"
    def get_queryset(self):
        qs = Poll.objects.annotate(cnt=Count('finished'))

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


class PopularUsersView(ListView):
    template_name = 'rambler/administrator/popular_users_list.html'
    context_object_name = 'instances'

    USERS_PER_PAGE = 1

    # "Администратор видит статистику
    # по самым популярным пользователям и опросам"
    def get_queryset(self):
        qs = PollUser.objects.annotate(cnt=Count('finished_polls'))

        paginator = Paginator(qs, self.USERS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


class UsersView(ListView):
    """Все пользователи"""
    template_name = 'rambler/administrator/users_list.html'
    context_object_name = 'instances'

    USERS_PER_PAGE = 1

    def get_queryset(self):
        qs = PollUser.objects.all()

        paginator = Paginator(qs, self.USERS_PER_PAGE)
        page = self.request.GET.get('page')

        users = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return users


class UserDetailView(UpdateView):
    """Редактирование пользователя"""
    model = PollUser
    template_name = 'rambler/form.html'
    fields = ['weight']
    success_url = '/administrator/users/'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        # чтобы показать, какой объект редактируется
        context['upper_object'] = self.get_object()
        return context
