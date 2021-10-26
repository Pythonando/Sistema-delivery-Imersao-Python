from django import template

register = template.Library()

@register.filter(name='enumerate')
def enumerat(valor):
    return enumerate(valor)