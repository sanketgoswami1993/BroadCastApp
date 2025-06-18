from django.conf.urls import patterns, url
from configure.views import configure_view, configure_view_all

urlpatterns = patterns('',
        url(r'^get/$', configure_view_all, name='configure-get-api'),
        url(r'^get/(?P<choice>[0-9]+)/$', configure_view, name='configure-get-choice-api'),
)