# -*- coding: utf-8 -*-

import httplib

from django.core.paginator import Paginator


STATUSES = {'OK': httplib.OK, 'ERROR': httplib.INTERNAL_SERVER_ERROR,
            'BAD_REQUEST': httplib.BAD_REQUEST}


class UpdateContextMixin(object):
    """Миксин
    Добавляет в контекст объект модели top_model
    Первичный ключ добавляемого объекта должен содержаться в
    self.kwargs['top_object_pk']
    """

    top_model = None

    def get_context_data(self, **kwargs):
        context = (super(UpdateContextMixin, self)
                   .get_context_data(**kwargs))
        obj = self.top_model.objects.get(pk=self.kwargs['top_object_pk'])
        context['upper_object'] = obj
        return context


class BootstrapFormMixin(object):
    """Миксин, который на все поля формы вешает bootstrap класс form-control"""
    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class PaginatorMixin(object):
    """Миксин для распределения объектов ListView по страницам
    """

    # Объектов на странице
    OBJECTS_PER_PAGE = None

    def get_page(self, qs):
        paginator = Paginator(qs, self.OBJECTS_PER_PAGE)
        page = self.request.GET.get('page')

        objects = (paginator.page(page) if page and page.isdigit()
                   else paginator.page(1))

        return objects

