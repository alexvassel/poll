# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from rambler.helpers import BootstrapFormMixin
from rambler.models import Poll, Question, Answer, PollUser


class PollForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Poll
        exclude = ['slug', 'user', 'created']


class QuestionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        exclude = ['poll']


class AnswerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Answer
        exclude = ['question']


class UserForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PollUser
        fields = ['weight']


class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    """Форма для регистрации нового пользователя
    работает с кастомной моделью User"""
    class Meta:
        model = PollUser
        fields = ('username',)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Переводим английские названия полей
        # а также убираем английские подсказки к полям
        self.fields['username'].label = u'Имя пользователя'
        self.fields['username'].help_text = ''
        self.fields['password1'].label = u'Пароль'
        self.fields['password2'].label = u'Повторите пароль'
        self.fields['password2'].help_text = ''


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Форма логина"""
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Переводим английские названия полей
        self.fields['username'].label = u'Имя пользователя'
        self.fields['password'].label = u'Пароль'


class FinishPollForm(forms.Form):
    """Форма сохранения pk завершаемого опроса"""
    poll_pk = forms.IntegerField()


class UserAnswerForm(forms.Form):
    """Форма сохранения данного пользователем ответа"""
    question_id = forms.IntegerField()
