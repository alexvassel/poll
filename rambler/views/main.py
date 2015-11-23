# -*- coding: utf-8 -*-

from django.http import JsonResponse

from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView, View)

from rambler.forms import PollForm, QuestionForm, AnswerForm
from rambler.helpers import get_context_mixin, STATUSES

from rambler.models import Poll, UserAnswers, Question, Answer


# Опросы
class PollListView(ListView):
    template_name = 'rambler/index.html'
    context_object_name = 'polls'

    def get_queryset(self):
        return Poll.objects.all().order_by('-weight', '-created__weight')


class PollDetailView(DetailView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/poll_details.html'


class PollTryView(PollDetailView):
    """Вывод шаблона для прохождения опроса,
    а также сохранение ответа на вопрос
    """
    template_name = 'rambler/try_poll.html'

    def get_context_data(self, **kwargs):
        context = super(PollTryView, self).get_context_data(**kwargs)
        # Сохраняем текущий опрос как начатый пользователем
        user = self.request.user.polluser
        poll = self.get_object()
        user.polls_in_progress.add(poll)
        return context

    def post(self, request, *args, **kw):
        """Записываем ответ пользоватля"""
        question_id = request.POST.get('question_id')
        answers_ids = (request.POST.getlist('answers_ids[]') or
                       request.POST.get('answers_ids'))

        answers_ids = (answers_ids if isinstance(answers_ids, list)
                       else [answers_ids])

        for answer_id in answers_ids:
            ua = UserAnswers(user=request.user.polluser,
                             poll=self.get_object(), question_id=question_id,
                             answer_id=answer_id)
            ua.save()

        return JsonResponse({'status': STATUSES['OK']})


class PollFinishView(View):
    """Помечаем опрос, как завершенный данным пользователем"""
    def post(self, request, *args, **kw):
        poll_pk = request.POST.get('poll_pk')
        user = self.request.user.polluser
        poll = Poll.objects.get(pk=poll_pk)

        # Опрос переходит из polls_in_progress в finished_polls
        user.polls_in_progress.remove(poll)
        user.finished_polls.add(poll)

        return JsonResponse({'status': STATUSES['OK']})


class UserPollListView(PollListView):
    template_name = 'rambler/user_polls.html'

    def get_queryset(self):
        return Poll.objects.filter(created=self.request.user.polluser)


class UserPollDetailView(PollDetailView):
    template_name = 'rambler/user_poll_details.html'


class PollCreateView(CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.created = self.request.user.polluser
        return super(PollCreateView, self).form_valid(form)


class PollUpdateView(UpdateView):
    model = Poll
    fields = ['name', 'weight']
    template_name = 'rambler/user_add_form.html'


class PollDeleteView(DeleteView):
    model = Poll

    def get_success_url(self):
        return '/{0}/polls/'.format(self.object.created.user.username)


# Вопросы

QuestionContextMixin = get_context_mixin(Poll)


class QuestionCreateView(QuestionContextMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.poll = Poll.objects.get(pk=self.kwargs['top_object_pk'])
        return super(QuestionCreateView, self).form_valid(form)


class QuestionUpdateView(QuestionContextMixin, UpdateView):
    model = Question
    fields = ['text', 'kind']
    template_name = 'rambler/user_add_form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return '/{0}/poll/{1}/'.format(self.object.poll.created.user.username,
                                       self.object.poll.pk)


# Ответы
AnswerContextMixin = get_context_mixin(Question)


class AnswerCreateView(AnswerContextMixin, CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.question = (Question.objects.
                                  get(pk=self.kwargs['top_object_pk']))
        return super(AnswerCreateView, self).form_valid(form)


class AnswerUpdateView(AnswerContextMixin, UpdateView):
    model = Answer
    fields = ['text']
    template_name = 'rambler/user_add_form.html'


class AnswerDeleteView(DeleteView):
    model = Answer

    def get_success_url(self):
        return '/{0}/poll/{1}/'.format(self.object.question.poll.
                                       created.user.username,
                                       self.object.question.poll.pk)
