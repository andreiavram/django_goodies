# coding: utf-8
'''
Created on Jul 3, 2012

@author: yeti
'''
from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.simple_tag(takes_context = True)
def context_menu(context):
    return render_to_string("goodies/context_menu.html", context)