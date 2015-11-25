# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm

from rambler.models import Poll, Question, Answer, PollUser


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        exclude = ['slug', 'user', 'created']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['poll']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ['question']


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя
    работает с кастомной моделью User
    """
    class Meta:
        model = PollUser
        fields = ("username",)
