from django import template

register = template.Library()


@register.filter
def percentage(value):
    """Return a float with 1 point of precision and a percent sign."""
    return format(value, ".1%")


@register.inclusion_tag('dashboard/_progress_report.html')
def progress_report(current, previous):
    """Display the change in progress from previous to current."""
    return {'current': current, 'previous': previous}
