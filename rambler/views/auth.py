# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator
from rambler.forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/registration/login/')

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
