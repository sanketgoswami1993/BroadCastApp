from django.conf.urls import patterns, include, url
from django.contrib import admin
from .import settings
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'broadcasting.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('info.urls')),
    url(r'^node/', include('node_hierarchy.urls')),
    url(r'^configure/', include('configure.urls')),
    url(r'^message/', include('message.urls')),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
