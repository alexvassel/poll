# -*- coding: utf-8 -*-
from django.http import JsonResponse

from django.views.generic import ListView, DetailView

from rambler.models import Poll, UserAnswers
from rambler import helpers


class PollListView(ListView):
    template_name = 'rambler/index.html'
    context_object_name = 'polls'

    def get_queryset(self):
        return Poll.objects.all().order_by('-weight', '-user__weight')


class PollDetailView(DetailView):
    model = Poll
    context_object_name = 'poll'
    template_name = 'rambler/poll_details.html'
    slug_field = 'slug'


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
