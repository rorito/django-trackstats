from django.conf.urls import url
from django.contrib import admin

from django.template.response import TemplateResponse

from trackstats.models import (
    Domain,
    Metric,
    Period,
    StatisticByDate,
    StatisticByDateAndObject)
from trackstats.admin.forms import (
    GraphByDateForm,
    GraphByDateAndObjectForm)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = (
        'ref',
        'name')


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    search_fields = (
        'ref',
        'name')
    list_display = (
        'ref',
        'name')
    list_filter = (
        'domain',)


class StatisticGraphMixin(object):
    graph_slug = None
    graph_form_class = None

    def get_urls(self):
        urls = super(StatisticGraphMixin, self).get_urls()
        custom_urls = [
            url('^graph/$', self.graph,
                name='trackstats_graph_' + self.graph_slug)
        ]
        return custom_urls + urls

    def graph(self, request):
        context = dict(
            self.admin_site.each_context(request))
        if 'to_date' in request.GET:
            form = self.graph_form_class(request.GET)
            if form.is_valid():
                stats = []
                for stat in form.get_statistics():
                    stats.append(
                        dict(
                            js_date='new Date({}, {}, {})'.format(
                                stat.date.year,
                                stat.date.month-1,
                                stat.date.day),
                            value=stat.value))
                context['statistics'] = stats
        else:
            stat = StatisticByDate.objects.last()
            initial = {}
            if stat:
                initial['metric'] = stat.metric
            form = self.graph_form_class(initial=initial)
        context['form'] = form
        return TemplateResponse(
            request,
            "trackstats/admin/{}/graph.html".format(self.graph_slug),
            context)


@admin.register(StatisticByDate)
class StatisticByDateAdmin(StatisticGraphMixin, admin.ModelAdmin):
    change_list_template = 'trackstats/admin/by_date/change_list.html'
    graph_slug = 'by_date'
    graph_form_class = GraphByDateForm

    ordering = (
        '-date',)
    list_display = (
        'date',
        'metric',
        'value'
    )
    date_hierarchy = 'date'

    list_filter = (
        'date',
        'period',
        'metric__domain',
        'metric')

    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('period__exact'):
            q = request.GET.copy()
            q['period__exact'] = str(Period.DAY)
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(StatisticByDateAdmin, self).changelist_view(request, extra_context=extra_context)


@admin.register(StatisticByDateAndObject)
class StatisticByDateAndObjectAdmin(StatisticGraphMixin, admin.ModelAdmin):
    change_list_template = (
        'trackstats/admin/by_date_and_object/change_list.html')
    graph_slug = 'by_date_and_object'
    graph_form_class = GraphByDateAndObjectForm
    ordering = (
        '-date',)
    list_display = (
        'date',
        'metric',
        'object_type',
        'object_id',
        'value'
    )
    date_hierarchy = 'date'

    list_filter = (
        'date',
        'period',
        'metric__domain',
        'metric')


    def changelist_view(self, request, extra_context=None):
        if not request.GET.has_key('period__exact'):
            q = request.GET.copy()
            q['period__exact'] = str(Period.DAY)
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super(StatisticByDateAndObjectAdmin, self).changelist_view(request, extra_context=extra_context)

#            stat = StatisticByDate.objects.last()
#            initial = {}
#            if stat:
#                initial['metric'] = stat.metric
#                initial['subject_type'] = stat.subject_type
#            form = GraphForm(initial=initial)
#        context['form'] = form
#        return TemplateResponse(
#            request,
#            "trackstats/admin/graphs.html",
#            context)
