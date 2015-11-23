# -*- coding: utf-8 -*-

from unidecode import unidecode

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify


class PollUser(models.Model):
    """Расширение стандартной модели User"""
    user = models.OneToOneField(User)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    polls_in_progress = models.ManyToManyField('Poll', blank=True, null=True,
                                               related_name='in_progress')
    finished_polls = models.ManyToManyField('Poll', blank=True, null=True,
                                            related_name='finished')

    def __unicode__(self):
        return u'{}'.format(self.user.username)


class Poll(models.Model):
    """
    """
    name = models.CharField(max_length=30, verbose_name=u'Имя')
    slug = models.SlugField(unique=True, max_length=30)
    weight = models.PositiveSmallIntegerField(verbose_name='Вес')
    user = models.ForeignKey(PollUser, blank=True, null=True)
    created = models.ForeignKey(PollUser, related_name='created_polls')

    def get_absolute_url(self):
        return '/{0}/poll/{1}/'.format(self.created.user.username, self.pk)

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.name))
        super(Poll, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{}'.format(self.name)

    def get_anonymous_url(self):
        return '/poll/{}/'.format(self.pk)


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
        return UserAnswers.objects.filter(user=user.polluser, question=self)

    def is_multiple(self):
        return True if self.kind == self.KIND_CHOICES[1][0] else False

    def get_absolute_url(self):
        return '/{0}/poll/{1}/'.format(self.poll.created.user.username, self.poll.pk)

    def __unicode__(self):
        return u'{}'.format(self.text)


class Answer(models.Model):
    """"""
    question = models.ForeignKey(Question, related_name='answers')
    text = models.TextField()

    def get_absolute_url(self):
        return '/{0}/poll/{1}/'.format(self.question.poll.created.user.username,
                                       self.question.poll.pk)

    def __unicode__(self):
        return u'{}'.format(self.text)


class UserAnswers(models.Model):
    """"Ответы конкретного пользователя"""
    poll = models.ForeignKey(Poll)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(PollUser)

    # TODO метод создания инстанса
    def __unicode__(self):
        return u'{}'.format(self.pk)
