from django.conf.urls import patterns, url
from message.views import message_view, message_create_view, social_view, message_delivery, message_category_view

urlpatterns = patterns('',
        url(r'^get/$', message_view, name='message-filter-api'),
        url(r'^category/get/$', message_category_view, name='message-category-api'),
        url(r'^get/(?P<pk>[0-9]+)/$', message_view, name='message-get-api'),
        url(r'^delivery/$', message_delivery, name='message-delivery-api'),
        url(r'^create/$', message_create_view, name='message-create-api'),
        url(r'^social/create/$', social_view, name='social-create-api'),
)