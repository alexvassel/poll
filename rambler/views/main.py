# -*- coding: utf-8 -*-
from django.db.models import Count

from django.http import JsonResponse

from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView, View, TemplateView)

from rambler.forms import PollForm, QuestionForm, AnswerForm
from rambler.helpers import STATUSES, UpdateContextMixin

from rambler.models import Poll, UserAnswer, Question, Answer


# Опросы
class PollDetailView(DetailView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/single-poll.html'


class PollTryView(PollDetailView):
    """Вывод шаблона для прохождения опроса,
    а также сохранение ответа на вопрос
    """
    template_name = 'rambler/try-poll.html'

    def get(self, request, *args, **kwargs):
        # Сохраняем текущий опрос как начатый пользователем
        user = self.request.user.polluser
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
            ua = UserAnswer(user=request.user.polluser,
                            question_id=question_id, aswer_id=answer_id)
            ua.save()

        return JsonResponse({'status': STATUSES['OK']})


class PollFinishView(View):
    """Помечаем опрос, как завершенный данным пользователем"""
    def post(self, request, *args, **kw):
        poll_pk = request.POST.get('poll_pk')
        user = self.request.user.polluser
        poll = Poll.objects.get(pk=poll_pk)

        # Опрос переходит из polls_in_progress в finished_polls
        # TODO транзакция (любой реквест в джанге - транзакция)
        user.polls_in_progress.remove(poll)
        user.finished_polls.add(poll)

        return JsonResponse({'status': STATUSES['OK']})


class PollListView(ListView):
    template_name = 'rambler/polls.html'
    context_object_name = 'polls'
    anonymous = False

    def get_queryset(self):
        qs = Poll.objects.order_by('-weight', '-created__weight')
        if self.anonymous:
            return qs
        return qs.filter(created=self.request.user.polluser)


class PollCreateView(CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'rambler/form.html'

    def form_valid(self, form):
        form.instance.created = self.request.user.polluser
        return super(PollCreateView, self).form_valid(form)


class PollUpdateView(UpdateView):
    model = Poll
    fields = ['name', 'weight']
    template_name = 'rambler/form.html'


class PollDeleteView(DeleteView):
    model = Poll

    def get_success_url(self):
        return '/polls/'.format(self.object.pk)


# Вопросы

class QuestionCreateView(UpdateContextMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'rambler/form.html'
    top_model = Poll

    def form_valid(self, form):
        form.instance.poll = Poll.objects.get(pk=self.kwargs['top_object_pk'])
        return super(QuestionCreateView, self).form_valid(form)


class QuestionUpdateView(UpdateContextMixin, UpdateView):
    model = Question
    top_model = Poll
    fields = ['text', 'kind']
    template_name = 'rambler/form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return '/poll/{0}/'.format(self.object.poll.pk)


# Ответы
class AnswerCreateView(UpdateContextMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'rambler/form.html'
    top_model = Question

    def form_valid(self, form):
        form.instance.question = (Question.objects.
                                  get(pk=self.kwargs['top_object_pk']))
        return super(AnswerCreateView, self).form_valid(form)


class AnswerUpdateView(UpdateContextMixin, UpdateView):
    model = Answer
    fields = ['text']
    template_name = 'rambler/form.html'
    top_model = Question


class AnswerDeleteView(DeleteView):
    model = Answer

    def get_success_url(self):
        return '/poll/{0}/'.format(self.object.question.poll.pk)


# TODO доделать
# Статистика
class UserStatView(TemplateView):
    template_name = 'rambler/stat.html'

    def get_context_data(self, **kwargs):
        context = super(UserStatView, self).get_context_data(**kwargs)
        user = self.request.user.polluser

        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        context['popular_polls'] = (Poll.objects.filter(created=user).
                                    annotate(cnt=Count('finished')).
                                    order_by('-cnt'))

        # Опросы по популярным ответам в процентном соотношении
        # от большего к меньшому
        context['polls_popular_by_answers'] = (Poll.objects.annotate
                                               (cnt=Count('questions__answers__useranswer')).
                                               order_by('-cnt'))
        return context
