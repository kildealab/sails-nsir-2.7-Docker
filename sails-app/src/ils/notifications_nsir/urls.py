from django.conf.urls import patterns, include, url
import views

# Table of contents for views provided in views.py (for notifications app)
urlpatterns = patterns('',
    url(r'^unsubscribe/(?P<incident_id>\d+)/$', views.Unsubscribe.as_view(), name="unsubscribe"),
    url(r'^subscribe/(?P<incident_id>\d+)/$', views.Subscribe.as_view(), name="subscribe"),
)

