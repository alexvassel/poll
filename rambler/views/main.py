# -*- coding: utf-8 -*-

from django.http import JsonResponse

from django.views.generic import (ListView, DetailView, CreateView,
                                  UpdateView, DeleteView)
from rambler.forms import PollForm, QuestionForm, AnswerForm

from rambler.models import Poll, UserAnswers, Question, Answer
from rambler import helpers


# Опросы
class PollListView(ListView):
    template_name = 'rambler/index.html'
    context_object_name = 'polls'

    def get_queryset(self):
        return Poll.objects.all().order_by('-weight', '-user__weight')


class PollDetailView(DetailView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/poll_details.html'


class TryPoll(PollDetailView):
    template_name = 'rambler/try_poll.html'

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

        return JsonResponse({'status': helpers.STATUSES['OK']})


class UserPollListView(PollListView):
    template_name = 'rambler/user_polls.html'

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user.polluser)


class UserPollDetailView(PollDetailView):
    template_name = 'rambler/user_poll_details.html'


class PollCreateView(CreateView):
    model = Poll
    form_class = PollForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user.polluser
        return super(PollCreateView, self).form_valid(form)


class PollUpdateView(UpdateView):
    model = Poll
    fields = ['name', 'weight']
    template_name = 'rambler/user_add_form.html'


class PollDeleteView(DeleteView):
    model = Poll

    def get_success_url(self):
        return '/my_polls/'


# Вопросы
class QuestionCreateView(CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.poll = Poll.objects.get(pk=self.kwargs['pk'])
        return super(QuestionCreateView, self).form_valid(form)

    # Добавляем в шаблон создания вопроса информацию о родительском опросе
    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        poll = Poll.objects.get(pk=self.kwargs['pk'])
        context['object'] = poll
        return context


class QuestionUpdateView(UpdateView):
    model = Question
    fields = ['text', 'kind']
    template_name = 'rambler/user_add_form.html'


class QuestionDeleteView(DeleteView):
    model = Question

    def get_success_url(self):
        return '/my_polls/poll/{}/'.format(self.object.poll.pk)


# Ответы
class AnswerCreateView(CreateView):
    model = Answer
    form_class = AnswerForm
    template_name = 'rambler/user_add_form.html'

    def form_valid(self, form):
        form.instance.question = Question.objects.get(pk=self.kwargs['q_pk'])
        return super(AnswerCreateView, self).form_valid(form)

    # Добавляем в шаблон создания ответа информацию о родительском вопросе
    def get_context_data(self, **kwargs):
        context = super(AnswerCreateView, self).get_context_data(**kwargs)
        question = Question.objects.get(pk=self.kwargs['q_pk'])
        context['object'] = question
        return context


class AnswerUpdateView(UpdateView):
    model = Answer
    fields = ['text']
    template_name = 'rambler/user_add_form.html'


class AnswerDeleteView(DeleteView):
    model = Answer

    def get_success_url(self):
        return '/my_polls/poll/{}/'.format(self.object.question.poll.pk)
