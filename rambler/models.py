# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db.models import Count

from unidecode import unidecode

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.template.defaultfilters import slugify


class PollUser(AbstractUser):
    """Расширение стандартной модели User"""
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    polls_in_progress = models.ManyToManyField('Poll', blank=True, null=True,
                                               related_name='in_progress')
    finished_polls = models.ManyToManyField('Poll', blank=True, null=True,
                                            related_name='finished')

    def get_absolute_url(self):
        return reverse('admin_user', args=[str(self.pk)])

    def __unicode__(self):
        return u'{}'.format(self.username)


class Poll(models.Model):
    """
    """
    name = models.CharField(max_length=30, verbose_name=u'Имя')
    slug = models.SlugField(unique=True, max_length=30, db_index=True)
    weight = models.PositiveSmallIntegerField(verbose_name='Вес',
                                              db_index=True)
    created = models.ForeignKey(PollUser, related_name='created_polls',
                                db_index=True)

    def get_absolute_url(self):
        return reverse('user_poll_details', args=[str(self.pk)])

    # TODO только если создаем объект
    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.name))
        super(Poll, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}'.format(self.name)


class Question(models.Model):
    """
    """
    KIND_CHOICES = (
        ('s', u'Один ответ'),
        ('m', u'Несолько ответов'),
    )
    poll = models.ForeignKey(Poll, related_name='questions')
    text = models.TextField()
    kind = models.CharField(max_length=1, choices=KIND_CHOICES)

    def answered(self, user):
        """Проверка на то, что данный пользователь уже ответил на вопрос
        """
        return UserAnswer.objects.filter(user=user, question=self)

    def is_multiple(self):
        return True if self.kind == self.KIND_CHOICES[1][0] else False

    def get_absolute_url(self):
        return reverse('user_poll_details', args=[str(self.poll.pk)])

    @property
    def popular_answers(self):
        """Опросы по популярным ответам в процентном соотношении
        от большего к меньшому"""
        answers = self.answers.all()
        popular = answers.annotate(cnt=Count('useranswers')).order_by('-cnt')
        return popular

    def __unicode__(self):
        return u'{}'.format(self.text)


class Answer(models.Model):
    """"""
    question = models.ForeignKey(Question, related_name='answers')
    text = models.TextField()

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

    # TODO метод создания инстанса
    def __unicode__(self):
        return u'{}'.format(self.pk)
