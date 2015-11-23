# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.assignment_tag(takes_context=True)
def answered(context, question):
    """Проверка на то, что текущий пользователь уже ответил на данный вопрос"""
    return question.answered(user=context['request'].user)
