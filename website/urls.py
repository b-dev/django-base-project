from django.conf import settings
from django.conf.urls import url, patterns, include

from django.contrib import admin
from .views import HomepageView

admin.autodiscover()

admin_patterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
)

website_patterns = patterns('',
    url(r'^$', HomepageView.as_view(), name='homepage'),
)

cms_patterns = patterns('',
    url(r'^', include('cms.urls')),
)

urlpatterns = admin_patterns + website_patterns

if settings.ENABLE_CMS:
    urlpatterns = admin_patterns + cms_patterns


if settings.DEBUG:
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns += patterns('',
            url(r'^__debug__/', include(debug_toolbar.urls)),
        )