# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.views.generic import (ListView, CreateView, UpdateView, DeleteView,
                                  View)
from django.views.generic.detail import SingleObjectMixin

from ..forms import (PollForm, QuestionForm, AnswerForm, FinishPollForm,
                     UserAnswerForm)
from ..helpers import STATUSES, UpdateContextMixin, PaginatorMixin
from ..models import Poll, UserAnswer, Question, Answer
from ..views.auth import LoggedInMixin


# Опросы
class PollDetailView(SingleObjectMixin, PaginatorMixin, ListView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'poll/single-poll.html'

    # Вопросов на странице
    OBJECTS_PER_PAGE = 5

    object = None

    def get_object(self, *args, **kw):
        return (Poll.objects.prefetch_related('questions__answers').
                get(pk=self.kwargs['pk']))

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(PollDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PollDetailView, self).get_context_data(**kwargs)
        context['instances'] = self.get_queryset()
        return context

    def get_queryset(self):
        qs = self.object.questions.all()

        return self.get_page(qs)


class PollTryView(LoggedInMixin, PollDetailView):
    """Вывод шаблона для прохождения опроса,
    а также сохранение ответа на вопрос
    """
    template_name = 'poll/try-poll.html'

    ERROR = 'Вы уже проходили данный опрос'

    def get(self, request, *args, **kwargs):
        user = request.user
        poll = self.get_object()

        # Два раза пользователь не может пройти тот же опрос
        if user.finished_polls.filter(id=poll.pk).exists():
            return HttpResponse(self.ERROR)

        # Сохраняем текущий опрос как начатый пользователем
        user.polls_in_progress.add(poll)

        return super(PollTryView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kw):
        """Записываем ответ пользователя"""
        form = UserAnswerForm(self.get_object().questions.all(), request.POST)

        if not form.is_valid():
            return JsonResponse({'status': STATUSES['ERROR']})

        question_pk = form.cleaned_data['question_pk']
        answers_pks = form.cleaned_data['answers_pks']

        for answer_pk in answers_pks:
            ua = UserAnswer(user=request.user,
                            question_id=question_pk, answer_id=answer_pk)
            ua.save()

        return JsonResponse({'status': STATUSES['OK']})

    def get_object(self, *args, **kw):
        return (Poll.objects.prefetch_related('questions__answers').
                get(slug=self.kwargs['slug']))


class PollFinishView(LoggedInMixin, View):
    """Помечаем опрос, как завершенный данным пользователем"""
    def post(self, request, *args, **kw):
        form = FinishPollForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'status': STATUSES['ERROR']})

        user = request.user
        poll = Poll.objects.get(pk=form.cleaned_data['poll_pk'])

        all_questions = poll.questions.count()

        # На все вопросы ответил пользователь?
        if all_questions != poll.answered_questions_count(user):
            return JsonResponse({'status': STATUSES['BAD_REQUEST']})

        # Опрос переходит из polls_in_progress в finished_polls
        with transaction.atomic():
            user.polls_in_progress.remove(poll)
            user.finished_polls.add(poll)

        return JsonResponse({'status': STATUSES['OK']})


class PollListView(PaginatorMixin, ListView):
    template_name = 'poll/polls.html'
    context_object_name = 'instances'
    # Этот класс отвечает за вывод опросов как для анонимных
    # так и для авторизованных пользователей
    anonymous = False

    # Опросов на странице
    OBJECTS_PER_PAGE = 10

    def get_queryset(self):
        qs = Poll.objects.order_by('-weight', '-created__weight')

        if not self.anonymous:
            qs = qs.filter(created=self.request.user)
            qs = qs.prefetch_related('in_progress', 'finished')

        return self.get_page(qs)


class PollCreateView(LoggedInMixin, CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'poll/form.html'

    def form_valid(self, form):
        form.instance.created = self.request.user
        return super(PollCreateView, self).form_valid(form)


class PollUpdateView(LoggedInMixin, UpdateView):
    model = Poll
    template_name = 'poll/form.html'
    form_class = PollForm


class PollDeleteView(LoggedInMixin, DeleteView):
    model = Poll

    def get_success_url(self):
        return reverse('index', args=[])


# Вопросы
class QuestionCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'poll/form.html'
    top_model = Poll

    def form_valid(self, form):
        # При создании записываем в инстанс
        # foreign key на верхнеуровневый объект (опрос)
        form.instance.poll = Poll.objects.get(pk=self.kwargs['top_object_pk'])
        return super(QuestionCreateView, self).form_valid(form)


class QuestionUpdateView(LoggedInMixin, UpdateContextMixin, UpdateView):
    model = Question
    top_model = Poll
    form_class = QuestionForm
    template_name = 'poll/form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return reverse('poll_details', args=[str(self.object.poll.pk)])


# Ответы
class AnswerCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'poll/form.html'
    top_model = Question

    def form_valid(self, form):
        # При создании записываем в инстанс
        # foreign key на верхнеуровневый объект (вопрос)
        form.instance.question = (Question.objects.
                                  get(pk=self.kwargs['top_object_pk']))
        return super(AnswerCreateView, self).form_valid(form)


class AnswerUpdateView(LoggedInMixin, UpdateContextMixin, UpdateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'poll/form.html'
    top_model = Question


class AnswerDeleteView(LoggedInMixin, DeleteView):
    model = Answer

    def get_success_url(self):
        return reverse('poll_details',
                       args=[str(self.object.question.poll.pk)])


# Статистика
class PopularPollsView(LoggedInMixin, PaginatorMixin, ListView):
    template_name = 'poll/stat/popular-polls.html'
    context_object_name = 'instances'

    # Опросов на странице
    OBJECTS_PER_PAGE = 10

    def get_queryset(self):
        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        qs = (Poll.objects.filter(created=self.request.user).
              annotate(cnt=Count('finished')).order_by('-cnt'))

        return self.get_page(qs)


class PopularAnswersView(LoggedInMixin, PaginatorMixin, ListView):
    """"Опросы по популярным ответам в процентном соотношении
    от большего к меньшому"""

    template_name = 'poll/stat/popular-answers.html'
    context_object_name = 'instances'

    # Опросов на странице
    OBJECTS_PER_PAGE = 1

    def get_queryset(self):
        qs = Poll.objects.filter(created=self.request.user)
        return self.get_page(qs)
