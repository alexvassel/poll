# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db.models import Count

from unidecode import unidecode

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify


class PollUser(AbstractUser):
    """Своя модель пользователя"""
    weight = models.PositiveSmallIntegerField(blank=True, null=True,
                                              verbose_name=u'Вес')
    # Хранение начатых пользователем опросов
    polls_in_progress = models.ManyToManyField('Poll', blank=True,
                                               related_name='in_progress')
    # Хранение завершенных пользователем опросов
    finished_polls = models.ManyToManyField('Poll', blank=True,
                                            related_name='finished')

    def get_absolute_url(self):
        return reverse('admin_user', args=[str(self.pk)])

    def __unicode__(self):
        return u'{}'.format(self.username)


class Poll(models.Model):
    name = models.CharField(max_length=30, verbose_name=u'Имя')
    slug = models.SlugField(unique=True, max_length=30, db_index=True)
    weight = models.PositiveSmallIntegerField(verbose_name='Вес',
                                              db_index=True)
    created = models.ForeignKey(PollUser, related_name='created_polls',
                                db_index=True)

    def get_absolute_url(self):
        return reverse('user_poll_details', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        # Созлаем slug транслитерацией имени
        self.slug = slugify(unidecode(self.name))
        super(Poll, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}'.format(self.name)


class Question(models.Model):
    # От типа зависит рендер ответа multiple select
    KIND_CHOICES = (
        ('s', u'Один ответ'),
        ('m', u'Несолько ответов'),
    )
    poll = models.ForeignKey(Poll, related_name='questions')
    text = models.TextField(verbose_name=u'Текст вопроса')
    kind = models.CharField(max_length=1, choices=KIND_CHOICES,
                            verbose_name=u'Тип вопроса')

    # Количество выводимых у опроса популярных ответов
    POPULAR_ANSWERS_COUNT = 3

    def answered(self, user):
        """Проверка на то, что данный пользователь уже ответил на вопрос
        """

        # Так как БД денормализована и в модели UserAnswer
        # есть ссылка на вопрос,
        # каждый раз, когда мы проверяем ответил ли пользователь на вопрос
        # мы обращаемся сразу к модели UserAnswer
        # а не ищем сначала по вопросу ответ
        return UserAnswer.objects.filter(user=user, question=self)

    def is_multiple(self):
        # Проверка типа вопроса
        return True if self.kind == self.KIND_CHOICES[1][0] else False

    def get_absolute_url(self):
        return reverse('user_poll_details', args=[str(self.poll.pk)])

    def popular_answers(self):
        """"Опросы по популярным ответам в процентном соотношении
        от большего к меньшому"""
        answers = self.answers.all()
        popular = (answers.annotate(percent=Count('useranswer') * 100 /
                   self.all_answers, cnt=Count('useranswer'))
                   .order_by('-percent')[:self.POPULAR_ANSWERS_COUNT])
        return popular

    @property
    def all_answers(self):
        return UserAnswer.objects.filter(question=self).count()

    def __unicode__(self):
        return u'{}'.format(self.text)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers')
    text = models.TextField(verbose_name=u'Текст ответа')

    def get_absolute_url(self):
        return reverse('user_poll_details', args=[str(self.question.poll.pk)])

    def __unicode__(self):
        return u'{}'.format(self.text)


class UserAnswer(models.Model):
    """"Ответы конкретного пользователя"""
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(PollUser)

    # Денормализация умышлена

    # позволяет избежать допзапроса при определении того,
    # отвечал ли пользователь на данный вопрос (Question.answered)
    question = models.ForeignKey(Question)

    def __unicode__(self):
        return u'{}'.format(self.pk)
