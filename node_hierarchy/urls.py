from django.conf.urls import patterns, url
from node_hierarchy.views import node_view, node_parent_view, node_all_view, node_multiple_view

urlpatterns = patterns('',
        url(r'^get/$', node_parent_view, name='node-detail-api'),
        url(r'^get-id-wise/$', node_multiple_view, name='node-multiple-api'),
        url(r'^get/all/$', node_all_view, name='node-all-api'),
        url(r'^get/(?P<pk>[0-9]+)/$', node_view, name='node-pk-api'),
)