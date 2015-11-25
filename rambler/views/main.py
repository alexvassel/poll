# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator

from django.http import JsonResponse

from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView, View)

from rambler.forms import PollForm, QuestionForm, AnswerForm
from rambler.helpers import STATUSES, UpdateContextMixin

from rambler.models import Poll, UserAnswer, Question, Answer


from rambler.views.auth import LoggedInMixin


# Опросы
class PollDetailView(DetailView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/single-poll.html'


class PollTryView(LoggedInMixin, PollDetailView):
    """Вывод шаблона для прохождения опроса,
    а также сохранение ответа на вопрос
    """
    template_name = 'rambler/try-poll.html'

    def get(self, request, *args, **kwargs):
        # Сохраняем текущий опрос как начатый пользователем
        user = request.user
        poll = self.get_object()
        user.polls_in_progress.add(poll)
        return super(PollTryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kw):
        """Записываем ответ пользователя"""

        question_id = request.POST.get('question_id')
        answers_ids = (request.POST.getlist('answers_ids[]') or
                       request.POST.get('answers_ids'))

        answers_ids = (answers_ids if isinstance(answers_ids, list)
                       else [answers_ids])
        for answer_id in answers_ids:
            ua = UserAnswer(user=request.user,
                            question_id=question_id, answer_id=answer_id)
            ua.save()

        return JsonResponse({'status': STATUSES['OK']})


class PollFinishView(LoggedInMixin, View):
    """Помечаем опрос, как завершенный данным пользователем"""
    def post(self, request, *args, **kw):
        poll_pk = request.POST.get('poll_pk')
        user = request.user
        poll = Poll.objects.get(pk=poll_pk)

        # Опрос переходит из polls_in_progress в finished_polls

        with transaction.atomic():
            user.polls_in_progress.remove(poll)
            user.finished_polls.add(poll)

        return JsonResponse({'status': STATUSES['OK']})


class PollListView(ListView):
    template_name = 'rambler/polls.html'
    context_object_name = 'instances'
    anonymous = False
    POLLS_PER_PAGE = 10

    def get_queryset(self):
        qs = Poll.objects.order_by('-weight', '-created__weight')

        if not self.anonymous:
            qs = qs.filter(created=self.request.user)

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


class PollCreateView(LoggedInMixin, CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'rambler/form.html'

    def form_valid(self, form):
        form.instance.created = self.request.user
        return super(PollCreateView, self).form_valid(form)


class PollUpdateView(LoggedInMixin, UpdateView):
    model = Poll
    fields = ['name', 'weight']
    template_name = 'rambler/form.html'


class PollDeleteView(LoggedInMixin, DeleteView):
    model = Poll

    def get_success_url(self):
        return '/polls/'.format(self.object.pk)


# Вопросы

class QuestionCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'rambler/form.html'
    top_model = Poll

    def form_valid(self, form):
        form.instance.poll = Poll.objects.get(pk=self.kwargs['top_object_pk'])
        return super(QuestionCreateView, self).form_valid(form)


class QuestionUpdateView(LoggedInMixin, UpdateContextMixin, UpdateView):
    model = Question
    top_model = Poll
    fields = ['text', 'kind']
    template_name = 'rambler/form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return '/poll/{0}/'.format(self.object.poll.pk)


# Ответы
class AnswerCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'rambler/form.html'
    top_model = Question

    def form_valid(self, form):
        form.instance.question = (Question.objects.
                                  get(pk=self.kwargs['top_object_pk']))
        return super(AnswerCreateView, self).form_valid(form)


class AnswerUpdateView(LoggedInMixin, UpdateContextMixin, UpdateView):
    model = Answer
    fields = ['text']
    template_name = 'rambler/form.html'
    top_model = Question


class AnswerDeleteView(LoggedInMixin, DeleteView):
    model = Answer

    def get_success_url(self):
        return '/poll/{0}/'.format(self.object.question.poll.pk)


# Статистика
class PopularPollsView(LoggedInMixin, ListView):
    template_name = 'rambler/stat/popular-polls.html'
    context_object_name = 'instances'

    POLLS_PER_PAGE = 10

    def get_queryset(self):
        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        qs = (Poll.objects.filter(created=self.request.user).
              annotate(cnt=Count('finished')).order_by('-cnt'))

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls


# Статистика
class PopularAnswersView(LoggedInMixin, ListView):
    """"Опросы по популярным ответам в процентном соотношении
        от большего к меньшому"""

    template_name = 'rambler/stat/popular-answers.html'
    context_object_name = 'instances'

    POLLS_PER_PAGE = 10

    def get_queryset(self):
        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        qs = Poll.objects.filter(created=self.request.user)

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls
