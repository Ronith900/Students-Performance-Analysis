from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.urls import reverse


class Term(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Subject(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    result = models.IntegerField(default=0, null=True, blank=True)
    total_hr_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, null=True, blank=True)

    def __str__(self):
        return '{0}-{1}'.format(self.name, self.term.name)


class Activities(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    activity_date = models.DateTimeField(default=now().date())
    hour_spent = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '{0}-{1}'.format(self.subject.term.name, self.subject.name)
