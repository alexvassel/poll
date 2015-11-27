# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.generic import (ListView, CreateView, UpdateView, DeleteView,
                                  View)
from django.views.generic.detail import SingleObjectMixin

from rambler.forms import (PollForm, QuestionForm, AnswerForm, FinishPollForm,
                           UserAnswerForm)
from rambler.helpers import STATUSES, UpdateContextMixin
from rambler.models import Poll, UserAnswer, Question, Answer
from rambler.views.auth import LoggedInMixin


# Опросы
class PollDetailView(SingleObjectMixin, ListView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/single-poll.html'

    QUESTION_PER_PAGE = 1

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

        paginator = Paginator(qs, self.QUESTION_PER_PAGE)
        page = self.request.GET.get('page')

        questions = (paginator.page(page) if page and page.isdigit()
                     else paginator.page(1))

        return questions


class PollTryView(LoggedInMixin, PollDetailView):
    """Вывод шаблона для прохождения опроса,
    а также сохранение ответа на вопрос
    """
    template_name = 'rambler/try-poll.html'

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
        form = UserAnswerForm(request.POST)

        if not form.is_valid():
            return JsonResponse({'status': STATUSES['ERROR']})

        question_id = form.cleaned_data['question_id']

        answers_ids = (request.POST.getlist('answers_ids[]') or
                       request.POST.get('answers_ids'))

        answers_ids = (answers_ids if isinstance(answers_ids, list)
                       else [answers_ids])

        for answer_id in answers_ids:
            ua = UserAnswer(user=request.user,
                            question_id=question_id, answer_id=answer_id)
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

        # На все вопросы ответил пользователь?
        if (poll.questions.count() !=
            UserAnswer.objects.filter(user=request.user,
                                      question=poll.questions.all()).count()):
            return JsonResponse({'status': STATUSES['BAD_REQUEST']})

        # Опрос переходит из polls_in_progress в finished_polls
        with transaction.atomic():
            user.polls_in_progress.remove(poll)
            user.finished_polls.add(poll)

        return JsonResponse({'status': STATUSES['OK']})


class PollListView(ListView):
    template_name = 'rambler/polls.html'
    context_object_name = 'instances'
    # Этот класс отвечает за вывод опросов как для анонимных
    # так и для авторизованных пользователей
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
    template_name = 'rambler/form.html'
    form_class = PollForm


class PollDeleteView(LoggedInMixin, DeleteView):
    model = Poll

    def get_success_url(self):
        return reverse('index', args=[])


# Вопросы
class QuestionCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'rambler/form.html'
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
    template_name = 'rambler/form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return reverse('poll_details', args=[str(self.object.poll.pk)])


# Ответы
class AnswerCreateView(LoggedInMixin, UpdateContextMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'rambler/form.html'
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
    template_name = 'rambler/form.html'
    top_model = Question


class AnswerDeleteView(LoggedInMixin, DeleteView):
    model = Answer

    def get_success_url(self):
        return reverse('poll_details',
                       args=[str(self.object.question.poll.pk)])


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


class PopularAnswersView(LoggedInMixin, ListView):
    """"Опросы по популярным ответам в процентном соотношении
    от большего к меньшому"""

    template_name = 'rambler/stat/popular-answers.html'
    context_object_name = 'instances'

    POLLS_PER_PAGE = 1

    def get_queryset(self):
        qs = Poll.objects.filter(created=self.request.user)

        paginator = Paginator(qs, self.POLLS_PER_PAGE)
        page = self.request.GET.get('page')

        polls = (paginator.page(page) if page and page.isdigit()
                 else paginator.page(1))

        return polls
