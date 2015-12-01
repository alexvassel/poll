# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .helpers import BootstrapFormMixin
from .models import Poll, Question, Answer, PollUser


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


class UserAnswerForm(BootstrapFormMixin, forms.Form):
    """Форма сохранения данного пользователем ответа"""
    question_pk = forms.IntegerField(widget=forms.HiddenInput())
    answers_pks = forms.ChoiceField(label='')

    select_field_name = 'answers_pks'

    def __init__(self, questions, *args, **kw):
        super(UserAnswerForm, self).__init__(*args, **kw)
        self.choices = [(a.pk, a.text) for a in (Answer.objects.filter
                                                 (question__in=
                                                  questions))]
        self._update_choices()

    def _update_choices(self):
        self.fields[self.select_field_name].choices = self.choices

    def prepare(self, user, question):
        """Подготовка формы для вывода на странице вопроса"""

        # Если пользователь уже ответил на вопрос, то disable его
        if question.answered(user):
            self._disable_field_widget()

        # Если возможно несколько ответов, то меняем тип select
        if question.is_multiple:
            self._change_field_widget()
            self._update_choices()

    def _disable_field_widget(self):
        self.fields[self.select_field_name].widget.attrs.update({'disabled':
                                                                 'disabled'})

    def _change_field_widget(self):
        # Необходимо сохранить атрибуты виджета для Bootstrap отображения
        # селекта
        widget_attrs = self.fields[self.select_field_name].widget.attrs
        self.fields[self.select_field_name].widget = (forms.SelectMultiple
                                                      (attrs=widget_attrs))
