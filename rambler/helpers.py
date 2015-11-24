# -*- coding: utf-8 -*-

import httplib

STATUSES = {'OK': httplib.OK}


class UpdateContextMixin(object):
    # Миксин
    # Добавляет в контекст объект модели top_model
    # Первичный ключ объекта должен содержаться в
    # self.kwargs['top_object_pk']

    top_model = None

    def get_context_data(self, **kwargs):
        context = (super(UpdateContextMixin, self)
                   .get_context_data(**kwargs))
        obj = self.top_model.objects.get(pk=self.kwargs['top_object_pk'])
        context['upper_object'] = obj
        return context
