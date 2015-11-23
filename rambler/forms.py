# -*- coding: utf-8 -*-

from django import forms

from rambler.models import Poll, Question, Answer


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
