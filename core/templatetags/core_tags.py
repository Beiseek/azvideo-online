from django import template

register = template.Library()

@register.filter(name='get_list')
def get_list(dict, key):
    """
    Custom template filter to return a list of values from a QueryDict.
    Usage: {{ request.GET|get_list:"genres" }}
    """
    return dict.getlist(key)
