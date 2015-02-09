from django.conf.urls import patterns, include, url
from django.contrib import admin
from goodies.svg_views import TestPlanner

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^testplanner/$', TestPlanner.as_view(), {}, "test_planner"),
)
