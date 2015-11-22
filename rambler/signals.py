# -*- coding: utf-8 -*-

# Создание вспомогательной записи после сохранения нового пользователя
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rambler.models import PollUser


def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = PollUser.objects.get_or_create(user=instance)

# Подключение к сигналу сохранения нового пользователя
post_save.connect(create_user_profile, sender=User)
