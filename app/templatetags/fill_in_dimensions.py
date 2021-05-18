from django import template

register = template.Library()


@register.filter()
def fill_height_width(value):
    value = value.replace("{width}", "70")
    value = value.replace("{height}", "70")
    return value
