# -*- coding: utf-8 -*-
from django.db.models import Count
from django.views.generic import ListView

from rambler.models import Poll


class PollsPopularView(ListView):
    template_name = 'rambler/poll_popular_stat.html'
    context_object_name = 'polls'

    def get_queryset(self):
        user = self.request.user.polluser

        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        data = (Poll.objects.filter(created=user).
                annotate(cnt=Count('finished'))).values()
        return data


class QuestionsPopularView(ListView):
    template_name = 'rambler/poll_popular_stat.html'
    context_object_name = 'polls'

    def get_queryset(self):
        user = self.request.user.polluser

        # "Опросы по популярности от самого популярного до менее популярных"
        # Сверху опросы, пройденные большим количеством пользователей
        data = (Poll.objects.filter(created=user).
                annotate(cnt=Count('finished')))
        return data
