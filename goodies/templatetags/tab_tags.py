# coding: utf-8
'''
Created on Jul 3, 2012

@author: yeti
'''
from django import template
from django.template.loader import render_to_string

register = template.Library()


def print_tabs(tabs, active_tab):
    return {'tabs': tabs, 'active_tab': active_tab}


register.inclusion_tag('goodies/tab_set.html')(print_tabs)


@register.simple_tag(takes_context=True)
def tab_js(context):
    return render_to_string("goodies/tab_navigation.html", context)