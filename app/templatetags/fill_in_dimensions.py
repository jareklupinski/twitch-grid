from django import template

register = template.Library()


@register.filter
def fill_in_dimensions(value):
    value = value.replace("{width}", "70")
    value = value.replace("{height}", "70")
    return value
