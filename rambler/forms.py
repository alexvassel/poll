# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from rambler.models import Poll, Question, Answer, PollUser


class BootstrapFormMixin(object):
    """Миксин, который на все поля формы вешает bootstrap класс form-control"""
    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


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
    работает с кастомной моделью User
    """
    class Meta:
        model = PollUser
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = u'Имя пользователя'
        self.fields['username'].help_text = ''
        self.fields['password1'].label = u'Пароль'
        self.fields['password2'].label = u'Повторите пароль'
        self.fields['password2'].help_text = ''


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = u'Имя пользователя'
        self.fields['password'].label = u'Пароль'
