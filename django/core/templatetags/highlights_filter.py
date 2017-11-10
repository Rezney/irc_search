from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()


@register.filter
def search_match2(text, string):
    if not string:
        return mark_safe(text)
    output = re.sub("(<[^>]*?%s[^>]*?>|%s)" % (string, string), lambda x:
                    '<mark style="background-color:Moccasin;">{}</mark>'.
                    format(string) if x.group(1)[0] != "<" else x.group(1),
                    text, flags=re.I | re.DOTALL)
    return mark_safe(output)


@register.filter
def search_match(text, string):
    if not string:
        return mark_safe(text)
    output = re.sub("(<[^>]*?%s[^>]*?>|%s)" % (string, string), lambda x:
                    '<mark style="background-color:LightBlue;">{}</mark>'.
                    format(string) if x.group(1)[0] != "<" else x.group(1),
                    text, flags=re.I | re.DOTALL)
    return mark_safe(output)
