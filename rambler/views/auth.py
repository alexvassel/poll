# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from rambler.forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('django.contrib.auth.views.login')

    else:
        form = CustomUserCreationForm()

    data = {}
    data.update(csrf(request))
    data['form'] = form

    return render(request, 'registration/start_registration.html', data)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class IsSuperuserMixin(object):
    """Проверка, что пользователь - superuser"""
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(IsSuperuserMixin, self).dispatch(*args, **kwargs)
