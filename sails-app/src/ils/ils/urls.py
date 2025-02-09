from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import RedirectView
from django.contrib import admin
from django.conf import settings
# from incidents_nsir.forms import CustomPasswordResetForm
admin.autodiscover()

urlpatterns = patterns('',
    # url('^', include('django.contrib.auth.urls')),
    url(r'^$', RedirectView.as_view(url=reverse_lazy(settings.DEFAULT_TAXONOMY + ":report")),name="home"),
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^password_reset/$', 'incidents_nsir.reset_views.password_reset', name="password_reset"),
    # url(r'^login/$', 'django.contrib.auth.views.login', name="login"),
    # url(r'^logout$', 'django.contrib.auth.views.logout',{'next_page':reverse_lazy("login")}, name="logout"),
    url(r'^nsir/', include('incidents_nsir.urls', namespace="incidents_nsir", app_name="incidents_nsir")),
    url(r'^notifications_nsir/', include('notifications_nsir.urls', namespace="notifications_nsir", app_name="notifications_nsir")),
    url(r'^comments/', include('fluent_comments.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout',{'next_page':reverse_lazy("login")}, name="logout"),
    url(r'^password_change/$', 'incidents_nsir.reset_views.password_change', name='password_change'),
    url(r'^password_change/done/$', 'incidents_nsir.reset_views.password_change_done', name='password_change_done'),
    url(r'^password_reset/$', 'incidents_nsir.reset_views.password_reset', name='password_reset'),
    url(r'^password_reset/done/$', 'incidents_nsir.reset_views.password_reset_done', name='password_reset_done'),
    # Support old style base36 password reset links; remove in Django 1.7
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'incidents_nsir.reset_views.password_reset_confirm_uidb36'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'incidents_nsir.reset_views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^reset/done/$', 'incidents_nsir.reset_views.password_reset_complete', name='password_reset_complete'),
    # The following urlconf allows access to media files (images uploaded to incidents)
    url(r'^media/incidentimages/(?P<filename>.*)$', 'incidents_nsir.views.protected_media')
)

# This method only works for serving media files on dev server. The production server
# can serve as well, but need to restrict access to files (only if logged in)
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)