from django import template

from members.models import Member

register = template.Library()

@register.filter
def get_prog_name(value):
    return Member.PROGRAMME_CHOICES[value]