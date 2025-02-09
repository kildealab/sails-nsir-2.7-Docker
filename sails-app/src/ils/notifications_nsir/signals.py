from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver, Signal
from django.contrib.sites.models import Site
from django.template import Context
from django.template.loader import get_template

import models

from accounts.models import ILSUser

#-----------------------------------------------------------------------------------------
# Signal definitions: 
# These signals will be used in other functions, and should provide the specified
# arguments. For example, the signal oncologist_submitted is called within the
# IncidentReport view of incidents_nsir/views.py
#-----------------------------------------------------------------------------------------
# Currently used:
incident_submitted = Signal(providing_args=["incident", "user", "subscribe"])
incident_completed = Signal(providing_args=["incident"])
oncologist_submitted = Signal(providing_args=["incident"])
investigator_assigned = Signal(providing_args=["incident"])
investigator_unassigned = Signal(providing_args=["incident"])
incident_invalid = Signal(providing_args=["incident", "comment"])
incident_reopened = Signal(providing_args=["incident", "comment"])
notify_managers = Signal(providing_args=["incident"])
action_assigned = Signal(providing_args=["action", "incident"])
action_completed = Signal(providing_args=["action", "incident"])

investigation_reminder = Signal(providing_args=["incident"])
action_reminder = Signal(providing_args=["action"])

# Currently unused:
# incident_actions = Signal(providing_args=["incident", "actions", "curs", "prevs"])
# incident_action_assigned = Signal(providing_args=["action"])
# incident_action_unassigned = Signal(providing_args=["action"])
incident_duplicate = Signal(providing_args=["incident", "duplicate"])
incident_shares = Signal(providing_args=["incident", "shares", "curs", "prevs"])
incident_share_assigned = Signal(providing_args=["share"])
incident_share_unassigned = Signal(providing_args=["share"])

#----------------------------------------------------------------------------------
# Sub-methods used in the various receiver functions defined below
#----------------------------------------------------------------------------------
def build_url(request, relative_path):
    """Build an absolute path name, given a relative path name and a request with META
    data required to build the absolute path.

    Args:
        request: a WSGIRequest object, which contains information needed to provide an
        absolute pathname.
        relative_path: a string represting the relative_path for which an absolute path
        is desired.

    Returns:
        A string representing an absolute URL.
    """
    if "HTTP_X_FORWARDED_HOST" not in request.META:
        return request.build_absolute_uri(relative_path)

    host = request.META["HTTP_X_FORWARDED_HOST"]
    http = 'https' if 'https' in request.META["wsgi.url_scheme"] or 'https' in request.META["HTTP_REFERER"] else 'http'
    return "%s://%s%s" % (http, host, relative_path)


def incident_url(request, incident):
    """Produce an absolute path name for the investigation page associated with a given 
    incident.

    Args:
        request: a WSGIRequest object, which contains information needed to provide an
        absolute pathname.
        incident: an Incident object, which we wish to build an absolute investigation
        URL for.

    Returns:
        A string representing the absolute URL of the investigation page to be accessed.
    """
    print build_url(request, incident.get_absolute_url())
    return build_url(request, incident.get_absolute_url())

def unsubscribe_url(request, incident):
    """Produce an absolute path name for the unsubscription page associated with a given 
    incident.

    Args:
        request: a WSGIRequest object, which contains information needed to provide an
        absolute pathname.
        incident: an Incident object, which we wish to build an absolute investigation
        URL for.

    Returns:
        A string representing the absolute URL of the unsubscription page to be accessed.
    """
    url = reverse("notifications_nsir:unsubscribe", kwargs={"incident_id":incident.incident_id})
    return build_url(request, url)


#-----------------------------------------------------------------------------------------
# The following functions are receiver functions. Takes sender argument and keyword
# arguments. Must accept kwargs b/c all signals send keyword arguments. The  @receiver()
# declaration is a decorator, which accepts the signal as an argument.
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Receive incident_submitted signals from any model. Create subscription instance for the
# submitting user (tied to their email). Generate and render a template with the relevant
# parameters inputted. Send email notification to the user IF they indicated desire to
# subscribe for notifications. Currently called within /incidents/views.py within the
# Report class, form_valid() functions. Send notice to submitting user.
#-----------------------------------------------------------------------------------------
@receiver(incident_submitted)
def incident_submitted_handler(sender, **kwargs ):

    incident = kwargs["incident"]
    user = kwargs["user"]
    subscribe = kwargs["subscribe"]
    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)
    if subscribe and user.email:
        sub = models.Subscription(user=user, incident=incident)
        sub.save()

    emails = [incident.submitted_by.email ] if incident.submitted_by.email else None
    if not emails:
        return

    template = get_template("notifications_nsir/email/incident_submitted.txt")
    context =  Context({"url":url, "incident":incident, "subscribe":subscribe, "user":user })
    subject = "SaILS - Incident #%d Submitted" % (incident.incident_id)
    content = template.render(context)
    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


@receiver(incident_completed)
def incident_completed_handler(sender, **kwargs ):
    """Send email notifications to all subscribed ILSUsers, for a particular incident/
    investigation, notifying that the investigation has been completed.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]
    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    # hold list of subscription objects tied to current incident:
    subs = models.Subscription.objects.filter(incident=incident)
    # hold list of email addresses corresponding to users with subscriptions to current incident:
    emails = subs.values_list("user__email",flat=True)

    template = get_template("notifications_nsir/email/incident_completed.txt")
    context =  Context({ "url":url, "unsubscribe":unsub_url, "incident":incident})
    subject = "SaILS - Investigation for Incident #%d Completed" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


@receiver(incident_invalid)
def incident_invalid_handler(sender, **kwargs):
    """Send email notifications to all subscribed ILSUsers, for a particular incident/
    investigation, notifying that the incident has been marked as invalid, and the 
    investigation has been closed.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]
    invalid_reason = kwargs["invalid_reason"]
    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    subs = models.Subscription.objects.filter(incident=incident)
    emails = subs.values_list("user__email", flat=True)
    template = get_template("notifications_nsir/email/incident_invalid.txt")
    context = Context({"url": url, "unsubscribe": unsub_url, "incident": incident, "invalid_reason":invalid_reason})
    subject = "SaILS - Incident #%d Closed" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


@receiver(incident_reopened)
def incident_reopened_handler(sender, **kwargs ):
    """Send email notifications to all subscribed ILSUsers, for a particular incident/
    investigation, notifying that an incident previously marked as invalid for trending, 
    has been re-opened.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]
    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    subs = models.Subscription.objects.filter(incident=incident)
    emails = subs.values_list("user__email",flat=True)
    template = get_template("notifications_nsir/email/incident_reopened.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "incident":incident })
    subject = "SaILS - Incident #%d Reopened" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

@receiver(notify_managers)
def notify_managers_handler(sender, **kwargs):
    """Send email notification to managers to notify them that an incident was reported.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]

    url = incident_url(sender.request, incident)

    for manager_username in settings.ILS_MANAGERS:
        try:
            manager = ILSUser.objects.get(username=manager_username)
            if manager != incident.investigator and manager != incident.oncologist:
                emails = [manager.email]
                template = get_template("notifications_nsir/email/notify_managers.txt")
                context = Context({ "url":url, "incident":incident, "manager":manager })
                subject = "SaILS - Incident #%d Manager Notification" % (incident.incident_id)
                content = template.render(context)

                send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)
       
        except (AttributeError, TypeError, ILSUser.DoesNotExist):
            continue

@receiver(oncologist_submitted)
def oncologist_submitted_handler(sender, **kwargs ):
    """Send email notification to the oncologist associated with a particular incident,
    notifying them that an incident report has been filed.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]

    # Only send if user is the investigator for the incident, and is subscribed for notifications
    if not (incident.oncologist):
        return

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    emails = [incident.oncologist.email]

    models.Subscription.objects.get_or_create(incident=incident, user=incident.oncologist)

    template = get_template("notifications_nsir/email/oncologist_submitted.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "incident":incident })
    subject = "SaILS - Incident #%d Oncologist Notification" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

@receiver(investigation_reminder)
def investigation_reminder_handler(sender, **kwargs):
    """Send an email notification to the current investigator of a particular incident,
    reminding them to complete the corresponding investigation.
    """
    incident = kwargs["incident"]

    # Only send if user is the investigator for the incident, and is subscribed for notifications
    if not (incident.investigator and incident.investigator.investigation_notifications):
        print "Reminder not sent for Incident #%d" % (incident.incident_id)
        return


    # Cannot create URLs in same fashion as other (synchronous) methods, because the task
    # which calls this signal does not have accest to an HTTP request object, and thus
    # there is no sender object passed to this. Instead use the Django Site framework
    # to get the domain name, and assuming HTTP protocol rather than HTTPS
    # url = incident_url(sender.request, incident)
    # unsub_url = unsubscribe_url(sender.request, incident)
    protocol = "http://"
    domain = Site.objects.get_current().domain
    inc_page = reverse("incidents_nsir:incident", kwargs={"incident_id": incident.incident_id})
    unsub_page = reverse("notifications_nsir:unsubscribe", kwargs={"incident_id":incident.incident_id})

    url = protocol + domain + inc_page
    unsub_url = protocol + domain + unsub_page

    emails = [incident.investigator.email]

    models.Subscription.objects.get_or_create(incident=incident, user=incident.investigator)

    template = get_template("notifications_nsir/email/investigation_reminder.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "incident":incident })
    subject = "SaILS - Incident #%d Investigation Reminder" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

    print "Reminder succesfully sent for Incident #%d" % (incident.incident_id)

@receiver(action_reminder)
def action_reminder_handler(sender, **kwargs):
    """Send an email notificaiton to the person responisble for a particular action, reminding
    them to complete the action.
    """
    action = kwargs["action"]
    incident = action.incident

    # Cannot create URLs in same fashion as other (synchronous) methods, because the task
    # which calls this signal does not have access to an HTTP request object, and thus
    # there is no sender object passed to this. Instead use the Django Site framework
    # to get the domain name, and assuming HTTP protocol rather than HTTPS
    # url = incident_url(sender.request, incident)
    # unsub_url = unsubscribe_url(sender.request, incident)
    protocol = "http://"
    domain = Site.objects.get_current().domain
    inc_page = reverse("incidents_nsir:incident", kwargs={"incident_id": incident.incident_id})

    url = protocol + domain + inc_page + "#actions-%d" % action.action_id

    emails = [action.responsible.email]

    template = get_template("notifications_nsir/email/action_reminder.txt")
    context = Context({ "url":url, "action":action, "incident":incident })
    subject = "SaILS - Incident #%d Action #%d Reminder" % (incident.incident_id, action.action_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)



@receiver(investigator_assigned)
def investigator_assigned_handler(sender, **kwargs ):
    """Send email notification to an ILSUser who has been selected as the investigator to
    follow up on a particular incident.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]

    # Only send if user is the investigator for the incident, and is subscribed for notifications
    if not (incident.investigator and incident.investigator.investigation_notifications):
        print "Investigator-assigned notification not sent for Incident #%d" % (incident.incident_id)
        return

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    # if incident.investigator.username == "dosimetry_group":
    #     dosi1 = ILSUser.objects.get(username="wparker")
    #     dosi2 = ILSUser.objects.get(username="ckaufmann")
    #     emails = [dosi1.email, dosi2.email]
    # else:
    #     emails = [incident.investigator.email]
    emails = [incident.investigator.email]

    models.Subscription.objects.get_or_create(incident=incident, user=incident.investigator)

    template = get_template("notifications_nsir/email/investigation_assigned.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "incident":incident })
    subject = "SaILS - Incident #%d Investigation Assigned" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

    print "Investigator-assigned notification succesfully sent for Incident #%d" % (incident.incident_id)


@receiver(investigator_unassigned)
def investigator_unassigned_handler(sender, **kwargs ):
    """Send email notification to an ILSUser who previously was the investigator for
    a particular incident, but is no longer the investigator.

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    incident = kwargs["incident"]
    old_investigator = kwargs["old_investigator"]

    #if old_investigator is None or not old_investigator.investigation_notifications:
    if old_investigator is None or not old_investigator.investigation_notifications:
        return

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    emails = [old_investigator.email]

    template = get_template("notifications_nsir/email/investigation_unassigned.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "incident":incident,'investigator':old_investigator })
    subject = "SaILS - Incident #%d Investigation Unassigned" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


@receiver(action_assigned)
def action_assigned_handler(sender, **kwargs ):
    """Send email notification to an ILSUser who has been assigned responsibility for an
    IncidentAction

    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    action = kwargs["action"]
    incident = kwargs["incident"]

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    emails = [action.responsible.email]

    models.Subscription.objects.get_or_create(incident=incident, user=action.responsible)

    template = get_template("notifications_nsir/email/action_assigned.txt")
    context = Context({ "url":url, "unsubscribe":unsub_url, "action":action, "incident":incident })
    subject = "SaILS - Incident #%d - Action #%d Assigned" % (incident.incident_id, action.action_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


@receiver(action_completed)
def action_completed_handler(sender, **kwargs ):
    """Send email notifications to all subscribed ILSUsers, for a particular incident/
    investigation, notifying that an action has been completed
    Args:
        sender: an IncidentInvestigation view object, from which the WSGI request can be
        extracted.
    """
    action = kwargs["action"]
    incident = kwargs["incident"]

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    # hold list of subscription objects tied to current incident:
    subs = models.Subscription.objects.filter(incident=incident)
    # hold list of email addresses corresponding to users with subscriptions to current incident:
    emails = subs.values_list("user__email",flat=True)

    template = get_template("notifications_nsir/email/action_completed.txt")
    context =  Context({ "url":url, "unsubscribe":unsub_url, "action":action, "incident":incident})
    subject = "SaILS - Incident #%d - Action #%d Completed" % (incident.incident_id, action.action_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


#=========================================================================================
# Currently unused signals
#=========================================================================================


#-----------------------------------------------------------------------------------------
# Receive incident_action_assigned signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send new investigator notice of assignment.
#-----------------------------------------------------------------------------------------
# @receiver(incident_action_assigned)
# def incident_action_assigned_handler(sender, **kwargs ):
#     action = kwargs["action"]
#     url = incident_url(sender.request, action.incident)
#     unsub_url = unsubscribe_url(sender.request, action.incident)

#     if action.responsible is None or not action.responsible.action_notifications:
#         return

#     models.Subscription.objects.get_or_create(incident=action.incident, user=action.responsible)

#     emails = [action.responsible.email]
#     template = get_template("notifications_nsir/email/incident_actions_assigned.txt")
#     context = Context({"url":url, "unsubscribe":unsub_url, "action":action, "incident":action.incident})
#     subject = "SaILS - Incident #%d Learning Action Assigned" % (action.incident.incident_id)
#     content = template.render(context)

#     send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

#-----------------------------------------------------------------------------------------
# Receive incident_action_unassigned signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send old investigator notice of unassignment.
#-----------------------------------------------------------------------------------------
# @receiver(incident_action_unassigned)
# def incident_action_unassigned_handler(sender, **kwargs ):
#     action = kwargs["action"]
#     old_responsible = kwargs["old_responsible"]
#     url = incident_url(sender.request, action.incident)
#     unsub_url = unsubscribe_url(sender.request, action.incident)

#     if old_responsible is None or not old_responsible.action_notifications:
#         return

#     emails = [action.responsible.email]
#     template = get_template("notifications_nsir/email/incident_actions_unassigned.txt")
#     context = Context({"url":url, "unsubscribe":unsub_url, "not_responsible": old_responsible, "action":action, "incident":action.incident})
#     subject = "SaILS - Incident #%d Learning Action Unassigned" % (action.incident.incident_id)
#     content = template.render(context)

#     send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


#-----------------------------------------------------------------------------------------
# Receive incident_actions signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send all subscribed users, except the current and previous investigators (who receive
# separate emails), notification of changes to incident actions (display which are
# complete and which are incomplete).
#-----------------------------------------------------------------------------------------
# @receiver(incident_actions)
# def incident_actions_handler(sender, **kwargs ):

#     incident = kwargs["incident"]
#     actions = kwargs["actions"]
#     curs = kwargs["curs"]
#     prevs = kwargs["prevs"]
#     complete = [a for a in actions if a.complete]
#     incomplete = [a for a in actions if not a.complete]

#     url = incident_url(sender.request, incident)
#     unsub_url = unsubscribe_url(sender.request, incident)

#     subs = models.Subscription.objects.filter(incident=incident)

#     emails = [s.user.email for s in subs if s.user.action_notifications and s.user not in curs and s.user not in prevs and s.user.email != '']
#     if not emails:
#         return

#     template = get_template("notifications_nsir/email/incident_actions.txt")
#     context = Context({
#         "incomplete":incomplete,
#         "complete":complete,
#         "incident":incident,
#         "investigation":incident.investigation,
#         "url": url,
#         "unsubscribe":unsub_url,
#     })
#     subject = "SaILS - Incident #%d Learning Actions Update" % (incident.incident_id)
#     content = template.render(context)

#     send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


#-----------------------------------------------------------------------------------------
# Receive incident_duplicate signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_duplicate() function.
# Send subscribed users notification that the incident has been marked as a duplicate of
# another incident within the database.
#-----------------------------------------------------------------------------------------
@receiver(incident_duplicate)
def incident_duplicate_handler(sender, **kwargs):
    incident = kwargs["incident"]
    duplicate = kwargs["duplicate"]
    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    subs = models.Subscription.objects.filter(incident=incident)
    emails = subs.values_list("user__email", flat=True)
    template = get_template("notifications_nsir/email/incident_duplicate.txt")
    context = Context({
        "url": url,
        "unsubscribe": unsub_url,
        "incident": incident,
        "investigation": incident.investigation,
        "duplicate": duplicate,
        "dup_inv": duplicate.investigation
    })
    subject = "SaILS - Incident #%d Closed" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


#-----------------------------------------------------------------------------------------
# Receive incident_share_assigned signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send new investigator notice of assignment.
#-----------------------------------------------------------------------------------------
@receiver(incident_share_assigned)
def incident_share_assigned_handler(sender, **kwargs ):
    share = kwargs["share"]
    url = incident_url(sender.request, share.incident)
    unsub_url = unsubscribe_url(sender.request, share.incident)

    if share.responsible is None or not share.responsible.action_notifications:
        return

    models.Subscription.objects.get_or_create(incident=share.incident, user=share.responsible)

    emails = [share.responsible.email]
    template = get_template("notifications_nsir/email/incident_shares_assigned.txt")
    context = Context({"url":url, "unsubscribe":unsub_url, "share":share, "incident":share.incident})
    subject = "SaILS - Incident #%d Sharing Action Assigned" % (share.incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

#-----------------------------------------------------------------------------------------
# Receive incident_share_unassigned signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send old investigator notice of unassignment.
#-----------------------------------------------------------------------------------------
@receiver(incident_share_unassigned)
def incident_share_unassigned_handler(sender, **kwargs ):
    share = kwargs["share"]
    old_responsible = kwargs["old_responsible"]
    url = incident_url(sender.request, share.incident)
    unsub_url = unsubscribe_url(sender.request, share.incident)

    if old_responsible is None or not old_responsible.action_notifications:
        return

    emails = [share.responsible.email]
    template = get_template("notifications_nsir/email/incident_shares_unassigned.txt")
    context = Context({"url":url, "unsubscribe":unsub_url, "not_responsible": old_responsible, "share":share, "incident":share.incident})
    subject = "SaILS - Incident #%d Sharing Action Unassigned" % (share.incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)


#-----------------------------------------------------------------------------------------
# Receive incident_shares signals from any model. Currently called within
# /incidents/views.py within the Incident class, handle_investigation_form() function.
# Send all subscribed users, except the current and previous investigators (who receive
# separate emails), notification of changes to incident shares (display which are complete
# and which are incomplete).
#-----------------------------------------------------------------------------------------
@receiver(incident_shares)
def incident_shares_handler(sender, **kwargs ):

    incident = kwargs["incident"]
    shares = kwargs["shares"]
    curs = kwargs["curs"]
    prevs = kwargs["prevs"]
    complete = [sh for sh in shares if sh.done]
    incomplete = [sh for sh in shares if not sh.done]

    url = incident_url(sender.request, incident)
    unsub_url = unsubscribe_url(sender.request, incident)

    subs = models.Subscription.objects.filter(incident=incident)
    emails = [s.user.email for s in subs if s.user.action_notifications and s.user not in curs and s.user not in prevs]
    if not emails:
        return

    template = get_template("notifications_nsir/email/incident_shares.txt")
    context = Context({
        "incomplete":incomplete,
        "complete":complete,
        "incident":incident,
        "investigation":incident.investigation,
        "url": url,
        "unsubscribe":unsub_url,
    })
    subject = "SaILS - Incident #%d Sharing Actions Update" % (incident.incident_id)
    content = template.render(context)

    send_mail(subject, content, settings.NOTIFICATIONS_EMAIL, emails, fail_silently=settings.NOTIFICATIONS_FAIL_SILENTLY)

