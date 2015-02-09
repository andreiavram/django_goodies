from django.http.response import HttpResponse
from django.views.generic.base import View
from goodies.svg import output_svg_planner

__author__ = 'yeti'



class TestPlanner(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="application/svg")
        response['Content-Disposition'] = 'attachment; filename="planner2015.pdf"'

        svg = output_svg_planner(output_format="buffer", file_format="pdf")
        response.write(svg)
        return response
