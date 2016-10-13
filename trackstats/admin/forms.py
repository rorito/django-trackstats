from datetime import timedelta, date

from django import forms
from django.contrib.contenttypes.models import ContentType

from trackstats.models import (
    Metric,
    Period,
    StatisticByDate,
    StatisticByDateAndObject)

DAY = 86400  # seconds
WEEK = DAY * 7
DAYS_28 = DAY * 28
MONTH = DAY * 30
LIFETIME = 0


class GraphByDateForm(forms.Form):
    statistic_model = StatisticByDate

    metric = forms.ModelChoiceField(queryset=None)
    period = forms.ChoiceField(initial=DAY)
    from_date = forms.DateField(initial=date.today() - timedelta(days=7))
    to_date = forms.DateField(initial=date.today())

    def __init__(self, *args, **kwargs):
        super(GraphByDateForm, self).__init__(*args, **kwargs)
        self.fields['metric'].queryset = Metric.objects.all()
        self.fields['period'].choices = ((DAY, 'Day'), (WEEK, 'Week'), (MONTH, 'Month'), (LIFETIME, 'Lifetime'))

    def get_statistics(self):
        assert self.is_valid()
        stats = self.statistic_model.objects.narrow(
            from_date=self.cleaned_data['from_date'],
            to_date=self.cleaned_data['to_date'],
            metric=self.cleaned_data['metric'],
            period=self.cleaned_data['period'])
        return stats.order_by('date')


class GraphByDateAndObjectForm(GraphByDateForm):
    statistic_model = StatisticByDateAndObject

    object_type = forms.ModelChoiceField(queryset=None, required=False)
    object_id = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(GraphByDateAndObjectForm, self).__init__(*args, **kwargs)
        self.fields['object_type'].queryset = ContentType.objects.all()

    def get_statistics(self):
        stats = super(GraphByDateAndObjectForm, self).get_statistics()
        stats = stats.filter(
            object_type=self.cleaned_data['object_type'])
        object_id = self.cleaned_data['object_id']
        if object_id:
            stats = stats.filter(object_id=object_id)
        return stats
