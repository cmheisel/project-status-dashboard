from dateutil.relativedelta import relativedelta

from django import template

register = template.Library()


@register.filter
def week_ending(value):
    """Return the Friday of the week of the date provided."""
    if not hasattr(value, "weekday"):
        return ""
    ending_date = value
    while ending_date.weekday() != 4:  # If not a friday
        ending_date = ending_date + relativedelta(days=1)
    return ending_date


@register.filter
def percentage(value):
    """Return a float with 1 point of precision and a percent sign."""
    return format(value, ".1%")


@register.filter
def subtract(value, arg):
    return value - arg


@register.filter
def absvalue(value):
    return abs(value)


@register.simple_tag
def google_sheet_url():
    from django.conf import settings
    return """https://docs.google.com/spreadsheets/d/{}/edit#gid=0""".format(settings.GOOGLE_SPREADSHEET_ID)


@register.inclusion_tag('dashboard/_progress_report.html')
def progress_report(current, previous):
    """Display the change in progress from previous to current."""

    context = {
        'current': current,
        'previous': previous,
        'scope_change': None,
        'complete_change': None,
    }

    if current and previous:
        if current.total < previous.total:
            context['scope_change'] = 'down'
        elif current.total > previous.total:
            context['scope_change'] = 'up'

        if current.pct_complete < previous.pct_complete:
            context['complete_change'] = 'down'
        elif current.pct_complete > previous.pct_complete:
            context['complete_change'] = 'up'

    return context
