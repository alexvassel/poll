# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from unidecode import unidecode


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
    name = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, max_length=30)
    weight = models.PositiveSmallIntegerField()
    user = models.ForeignKey(PollUser)

    def get_absolute_url(self):
        return '/poll/{}/'.format(self.slug)

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
        return UserAnswers.objects.filter(user=user.polluser, question=self)

    def is_multiple(self):
        return True if self.kind == self.KIND_CHOICES[1][0] else False

    def __unicode__(self):
        return u'{}'.format(self.pk)


class Answer(models.Model):
    """"""
    question = models.ForeignKey(Question, related_name='answers')
    text = models.TextField()

    def __unicode__(self):
        return u'{}'.format(self.pk)


class UserAnswers(models.Model):
    """"Ответы конкретного пользователя"""
    poll = models.ForeignKey(Poll)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
    user = models.ForeignKey(PollUser)

    # TODO метод создания инстанса
    def __unicode__(self):
        return u'{}'.format(self.pk)
