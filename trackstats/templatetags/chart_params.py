from datetime import datetime, timedelta
from django import template
from trackstats.models import Metric

register = template.Library()

DATE_FORMAT = '%Y-%m-%d'


@register.simple_tag(takes_context=True)
def url_redirect_params(context):
    request = context.get('request', {})
    GET = getattr(request, 'GET', {})
    try:
        metric = int(GET.get('metric__id__exact'))
        if Metric.objects.filter(pk=metric).count() == 0:
            raise ValueError("Not metric")
    except (ValueError, AssertionError, TypeError):
        # If there's no metic selected, there's no need to look for the dates
        return ''

    from_date, to_date = None, None
    query = ''

    try:
        if 'date__year' in GET and 'date__month' in GET:

            year = int(GET.get('date__year'))
            month = int(GET.get('date__month'))

            if 'date__day' in GET:
                day = int(GET.get('date__day'))
                from_date = to_date = datetime(year, month, day)
            else:

                from_date = datetime(year, month, 1)
                if month == 12:
                    to_date = datetime(year + 1, 1, 1)
                else:
                    to_date = datetime(year, month + 1, 1)
                to_date -= timedelta(days=1)

        else:
            from_date = datetime.strptime(GET.get('date__gte'), DATE_FORMAT)
            to_date = datetime.strptime(GET.get('date__lt'), DATE_FORMAT)
    except (ValueError, TypeError):
        # Some date range must have been wrong
        pass

    if from_date and to_date:
        query = (
            '?from_date={from_date}'
            '&to_date={to_date}'
            '&metric={metric}'
        ).format(
            metric=metric,
            from_date=from_date.strftime(DATE_FORMAT),
            to_date=to_date.strftime(DATE_FORMAT)
        )

    return query


@register.simple_tag(takes_context=True)
def get_chart_button_title(context):
    request = context.get('request', {})
    GET = getattr(request, 'GET', {})
    metric = GET.get('metric__id__exact')
    if metric:
        return "Plot this query!"
    else:
        return "Plot a metric selecting one from the list at the bottom."
