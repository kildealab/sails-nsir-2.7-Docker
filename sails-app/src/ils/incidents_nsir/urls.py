from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^report/$', views.IncidentReport.as_view(), name="report"),
    url(r'^dashboard/$', views.Dashboard.as_view(), name="dashboard"),
    # url(r'^news/$', views.News.as_view(), name="news"),
    url(r'^incident/(?P<incident_id>\d+)/$', views.IncidentInvestigation.as_view(), name="incident"),

    url(r'^search/$',views.Search.as_view(), name="search"),
    url(r'^incident-summary/(?P<incident_id>\d+)/$', views.IncidentSummary.as_view(), name="incident-summary"),

    url(r'^change-event-type/(?P<incident_id>\d+)/$', views.ChangeEventType.as_view(), name="change-event-type"),

    # Investigation Lists
    url(r'^triage/$', views.TriageIncidentsList.as_view(), name="triage-incidents"),
    url(r'^incomplete-incidents/$', views.IncompleteIncidentsList.as_view(), name="incomplete-incidents"),
    url(r'^flagged-incidents/$', views.IncompleteAndFlaggedIncidentsList.as_view(), name="flagged-incidents"),
    url(r'^all-flagged-incidents/$', views.FlaggedIncidentsList.as_view(), name="all-flagged-incidents"),
    url(r'^complete-incidents/$', views.CompleteIncidentsList.as_view(), name="complete-incidents"),
    url(r'^actual-incidents/$', views.ActualIncidentsList.as_view(), name="actual-incidents"),
    url(r'^invalid-incidents/$', views.InvalidIncidentsList.as_view(), name="invalid-incidents"),
    url(r'^all-incidents/$', views.AllIncidentsList.as_view(), name="all-incidents"),
    # User Investigation lists
    url(r'^my-incidents/$', views.MyIncidentsList.as_view(), name="my-incidents"),
    url(r'^my-investigations/$', views.MyInvestigationsList.as_view(), name="my-investigations"),
    url(r'^my-patients/$', views.MyPatientsList.as_view(), name="my-patients"),

    # Action Lists
    url(r'^incomplete-actions/$', views.IncompleteActionsList.as_view(), name="incomplete-actions"),
    url(r'^complete-actions/$', views.CompleteActionsList.as_view(), name="complete-actions"),
    url(r'^all-actions/$', views.AllActionsList.as_view(), name="all-actions"),
    # User Action lists
    url(r'^my-assigned-by-actions/$', views.AssignedByActionsList.as_view(), name="my-assigned-by-actions"),
    url(r'^my-responsible-actions/$', views.ResponsibleActionsList.as_view(), name="my-responsible-actions"),
    url(r'^my-completed-actions/$', views.MyCompleteActionsList.as_view(), name="my-completed-actions"),

    # Sharing Lists
    url(r'^incomplete-sharing/$', views.IncidentReport.as_view(), name="incomplete-sharing"),
    url(r'^complete-sharing/$', views.IncidentReport.as_view(), name="complete-sharing"),
    url(r'^all-sharing/$', views.IncidentReport.as_view(), name="all-sharing"),
    # User Share lists
    url(r'^my-incomplete-sharing/$', views.IncidentReport.as_view(), name="my-incomplete-sharing"),
    url(r'^my-complete-sharing/$', views.IncidentReport.as_view(), name="my-complete-sharing"),
    url(r'^my-sharing/$', views.IncidentReport.as_view(), name="my-sharing"),

    # Statistics
    url(r'^statistics/$', views.Statistics.as_view(), name="statistics"),
    url(r'^incomplete-statistics/$', views.IncidentReport.as_view(), name="incomplete-statistics"),

    url(r'^reload_fk_choices.html$', views.reload_fk_choices_view, name="reload_fk_choices"),
    url(r'^reload_user_choices.html$', views.reload_user_choices_view, name="reload_user_choices"),
    url(r'^get_field_values.html$', views.get_field_values_view, name="get_field_values"),
    url(r'^save_new_template.html$', views.save_new_template_view, name="save_new_template"),
    url(r'^save_new_image.html$', views.save_new_image_view, name="save_new_image"),

    # AJAX urls
    # url(r'^ajax/$', views.ajax_view, name='ajax'),
)
