# -*- coding: utf-8 -*-

from django import template

from poll.forms import UserAnswerForm


register = template.Library()


@register.inclusion_tag('rambler/parts/question-form.html', takes_context=True)
def get_form(context, question):
    """Вывод формы для вопроса"""
    user = context['request'].user
    form = UserAnswerForm([question], initial={'question_pk': question.pk})
    # Подготавливаем форму к отображению на странице
    form.prepare(user, question)
    return {'form': form}
