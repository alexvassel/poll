# -*- coding: utf-8 -*-

STATUSES = {'OK': 200}


# Функция возвращает класс-миксин, в зависимости от переданной модели
def get_context_mixin(model):
    # Класс для обновления контекста
    # Добавляет в контекст объект-обертку
    # (объект, в который вложен текущий инстанс)
    # (для вопроса - опрос, для ответа - вопрос)
    class UpdateContextMixin(object):
        # Миксин
        # Добавляем в шаблон создания вопроса информацию о родительском объекте
        # Первичный ключ объекта должен содержаться в
        # self.kwargs['top_object_pk']
        def get_context_data(self, **kwargs):
            context = (super(UpdateContextMixin, self)
                       .get_context_data(**kwargs))
            obj = model.objects.get(pk=self.kwargs['top_object_pk'])
            context['upper_object'] = obj
            return context

    return UpdateContextMixin
