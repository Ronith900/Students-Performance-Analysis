from django.shortcuts import render, redirect
from .forms import UserRegisterForm, CreateTerm, ResultForm
from django.views.generic import TemplateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from decimal import Decimal
from collections import OrderedDict
import datetime


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term = {}
        for tr in Term.objects.filter(user=self.request.user).order_by('id'):
            term[tr] = list()
            for subjects in Subject.objects.filter(term=tr):
                term[tr].append(subjects)

        context['term'] = term
        return context


class TermDetail(LoginRequiredMixin, DetailView):
    model = Term

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subjects'] = Subject.objects.filter(term=self.get_object()).order_by('-total_hr_spent')
        print(context['subjects'])
        print(Activities.objects.filter(subject=context['subjects'][0]).count())
        daily_hustle = OrderedDict()
        subj_name = []
        for activity in Activities.objects.filter(subject__term=self.get_object()).order_by('-activity_date',
                                                                                            'subject__name',
                                                                                            '-hour_spent'):
            if activity.activity_date not in daily_hustle:
                daily_hustle[activity.activity_date] = OrderedDict()
                daily_hustle[activity.activity_date]['tot_hrs'] = 0
            daily_hustle[activity.activity_date][activity.subject.name] = activity.hour_spent
            daily_hustle[activity.activity_date]['tot_hrs'] += activity.hour_spent
            if activity.subject.name not in subj_name:
                subj_name.append(activity.subject.name)

        print(daily_hustle)
        context['daily_hustle'] = daily_hustle
        context['subj_name'] = subj_name
        return context

    def post(self, request, **kwargs):
        for subj in Subject.objects.filter(term=self.get_object()):
            hrs_spent = Decimal(request.POST.get(str(subj.id)))
            subj.total_hr_spent = hrs_spent + subj.total_hr_spent
            subj.save()

            activ_obj, activ_created = Activities.objects.get_or_create(subject=subj, activity_date=now().date(),
                                                                        defaults={'hour_spent': hrs_spent})

            if (activ_created):
                print('New object created')
            else:
                activ_obj.hour_spent = activ_obj.hour_spent + hrs_spent

            activ_obj.save()
        return redirect('/term/' + str(self.get_object().id))


class ResultUpdateForm(LoginRequiredMixin, UpdateView):
    model = Subject
    fields = ['result']
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse('term-detail', kwargs={'pk': self.object.term.pk})


class AnalyseTerm(LoginRequiredMixin, DetailView):
    model = Term
    template_name = 'term_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term_data = dict()
        for subject in Subject.objects.filter(term=self.get_object()):
            if 'subjects' not in term_data:
                term_data['subjects'] = list()
                term_data['hrs_spent'] = list()
                term_data['actual_result'] = list()
            term_data['subjects'].append(subject.name)
            term_data['hrs_spent'].append(subject.total_hr_spent)
            term_data['actual_result'].append(subject.result)

        context['data'] = term_data
        return context


class DailyAnalysis(LoginRequiredMixin, DetailView):
    model = Term
    template_name = 'daily_analysis.html'
    colrs = ['red', 'blue', 'orange', 'green', 'purple', 'grey']
    count = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        temp_dict = {'date': list(), 'subjects': dict()}
        for act in Activities.objects.filter(subject__term=self.get_object()).order_by('-activity_date'):
            if act.activity_date.date() not in temp_dict['date']:
                temp_dict['date'].append(act.activity_date.date())
            if act.subject.name not in temp_dict['subjects']:
                temp_dict['subjects'][act.subject.name] = {'bg_color': self.colrs[self.count], 'tot_hrs': list()}
                self.count += 1
            temp_dict['subjects'][act.subject.name]['tot_hrs'].append(act.hour_spent)

        context['data'] = temp_dict
        print(temp_dict)
        return context


class TermDelete(LoginRequiredMixin, DeleteView):
    model = Term
    success_url = '/'


class EditDailyActivity(LoginRequiredMixin, TemplateView):
    template_name = 'alpha/edit_daily_activity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_str = str(self.kwargs['year']) + '-' + str(self.kwargs['month']) + '-' + str(self.kwargs['day'])
        date_time_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        context['activity_date'] = date_time_obj.date()
        context['activities'] = Activities.objects.filter(activity_date=date_time_obj,subject__term=self.kwargs['pk'])
        context['total_hrs'] = 0
        for act in context['activities']:
            context['total_hrs'] += act.hour_spent
        return context

    def post(self, request, **kwargs):
        date_str = str(self.kwargs['year']) + '-' + str(self.kwargs['month']) + '-' + str(self.kwargs['day'])
        date_time_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        for act in Activities.objects.filter(activity_date=date_time_obj,subject__term=self.kwargs['pk']):
            actual_hrs = act.hour_spent
            print(request.POST.get(str(act.id)))
            if Decimal(request.POST.get(str(act.id))) != actual_hrs:
                difference = Decimal(request.POST.get(str(act.id))) - actual_hrs
                act.hour_spent = Decimal(request.POST.get(str(act.id)))
                subject = act.subject
                act.save()
                if difference > 0:
                    subject.total_hr_spent +=difference
                else:
                    subject.total_hr_spent -= abs(difference)
                subject.save()

        return redirect('/term/' + str(self.kwargs['pk']))


class About(LoginRequiredMixin, TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = 'About page :)'
        return context


def register(request):
    if request.method == 'POST':
        # create a form instance from POST data.
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'alpha/register.html', {'form': form, 'title': request.user.username})


def create_term(request):
    if request.method == 'POST':
        # create a form instance from POST data.
        form = CreateTerm(request.POST)
        if form.is_valid():
            term = Term()
            term.name = form.cleaned_data.get('term')
            term.user = request.user
            term.save()

            for subject in form.cleaned_data.get('subjects').split(','):
                subj = Subject()
                subj.name = subject
                subj.term = term
                subj.save()

        return redirect('index')
    else:
        form = CreateTerm()
    return render(request, 'alpha/create_term.html', {'form': form, 'title': request.user.username})
