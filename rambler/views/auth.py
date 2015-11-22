# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.template.context_processors import csrf
from django.utils.decorators import method_decorator


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/registration/login/')

    else:
        form = UserCreationForm()

    data = {}
    data.update(csrf(request))
    data['form'] = form

    return render(request, 'registration/start_registration.html', data)


class LoggedInMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)
