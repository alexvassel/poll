# -*- coding: utf-8 -*-

from django.contrib import admin

from models import Poll, Question, Answer, UserAnswers, PollUser


class PollAdmin(admin.ModelAdmin):
    pass


class QuestionAdmin(admin.ModelAdmin):
    pass


class AnswerAdmin(admin.ModelAdmin):
    pass


class UserAnswersAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(UserAnswers, UserAnswersAdmin)
admin.site.register(PollUser, UserProfileAdmin)

