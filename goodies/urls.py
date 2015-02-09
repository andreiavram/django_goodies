__author__ = 'andrei'

from django.conf.urls import patterns
from goodies.views import TagsJson, TestPlanner
from goodies.views import GenericDeleteJavaScript,\
    GenericTabDeleteJavaScript


urlpatterns = patterns('goodies.views',
   (r'js/(?P<app_label>\w+)/(?P<model>\w+)/delete.js$', GenericDeleteJavaScript.as_view(), {}, "js_delete"),
   (r'js/tabs/(?P<app_label>\w+)/(?P<model>\w+)/delete.js$', GenericTabDeleteJavaScript.as_view(), {}, "js_tab_delete"),
    (r'ajax/tags/$', TagsJson.as_view(), {}, "tag_list"),
)
