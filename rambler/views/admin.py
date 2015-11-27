# -*- coding: utf-8 -*-

from decimal import Decimal, getcontext

from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView, ListView, UpdateView

from ..forms import UserForm
from ..models import Poll, PollUser, Question, UserAnswer
from .auth import IsSuperuserMixin


class StatView(IsSuperuserMixin, TemplateView):
    """Статистика, видная админу"""
    template_name = 'rambler/administrator/common_stat.html'

    def get_context_data(self, **kwargs):
        context = super(StatView, self).get_context_data(**kwargs)

        # Максимальная точность (количество цифр)
        # результата арифметических операций с Decimal
        getcontext().prec = 3

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
        context['average_poll_user'] = (Decimal(all_polls) /
                                        all_users) if all_users else 0
        context['average_answers_user'] = (Decimal(all_answers) /
                                           all_users) if all_users else 0
        context['average_answers_poll'] = (Decimal(all_answers) /
                                           all_polls) if all_polls else 0
        context['popular_users'] = (PollUser.objects.annotate(
                                    cnt=Count('finished_polls')))
        return context


class PopularPollsView(IsSuperuserMixin, ListView):
    template_name = 'rambler/administrator/popular_polls_list.html'
    context_object_name = 'instances'

    POLLS_PER_PAGE = 10

    # "Администратор видит статистику
    # по самым популярным опросам"
    def get_queryset(self):
        qs = Poll.objects.annotate(cnt=Count('finished'))

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


class PopularUsersView(IsSuperuserMixin, ListView):
    template_name = 'rambler/administrator/popular_users_list.html'
    context_object_name = 'instances'

    USERS_PER_PAGE = 10

    # "Администратор видит статистику
    # по самым популярным пользователям"
    def get_queryset(self):
        qs = PollUser.objects.annotate(cnt=Count('finished_polls'))

        paginator = Paginator(qs, self.USERS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


class UsersView(IsSuperuserMixin, ListView):
    """Все пользователи"""
    template_name = 'rambler/administrator/users.html'
    context_object_name = 'instances'

    USERS_PER_PAGE = 10

    def get_queryset(self):
        qs = PollUser.objects.all()

        paginator = Paginator(qs, self.USERS_PER_PAGE)
        page = self.request.GET.get('page')

        users = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return users


class UserDetailView(IsSuperuserMixin, UpdateView):
    """Редактирование пользователя"""
    model = PollUser
    template_name = 'rambler/form.html'
    form_class = UserForm
    success_url = '/administrator/users/'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        # чтобы показать, какой объект редактируется
        context['upper_object'] = self.get_object()
        return context
