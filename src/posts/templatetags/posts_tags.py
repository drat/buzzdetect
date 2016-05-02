from django import template


register = template.Library()


@register.filter
def seconds_since(dt1, dt2):
    return (dt1 - dt2).seconds
