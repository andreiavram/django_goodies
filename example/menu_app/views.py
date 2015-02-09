from django.shortcuts import render

# Create your views here.
from django.views.generic.base import TemplateView


class TestContextMenu(TemplateView):
    template_name = "context_menu_test.html"
