from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, FieldError, ValidationError
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.db.models import Q, Max, FieldDoesNotExist
from django.db.models.loading import get_model
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.utils import formats, timezone
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, TemplateView, FormView

from listable.views import BaseListableView, SELECT
from listable.views import Column as C

import operator
import os
import json
import collections
import datetime
import time
import re
from time import strftime

import forms
import models
import feeds
import statistics
from notifications_nsir import signals
from accounts.models import ILSUser

import subprocess

#-----------------------------------------------------------------------------------------
# View constants:
# BASE_TEMPLATE - base template to inherit from
# USER - current SaILS user
# MONTHS - array of months used for formatting purposes (Dashboard view)
# MIN/MAX_ONLINE_ID - identify the range of ID numbers set aside for online reports
#-----------------------------------------------------------------------------------------
BASE_TEMPLATE = "incidents_nsir/base_nsir.html"
User = get_user_model()
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MIN_ONLINE_ID = 100000
MAX_ONLINE_ID = 200000

#-----------------------------------------------------------------------------------------
# Abstract Views & Mixins
#-----------------------------------------------------------------------------------------
class StaffRequiredMixin(object):
    """Raise authorization error if user is anonymous (not logged in).

    Parent class (not standalone) which provides condition on the dispatch() method; only
    allow processing of the desired GET/POST if the user has appropriate change_incident
    permissions. Note overrides the default dispatch() method for object class.
    """
    def dispatch(self, request, *args, **kwargs):
        #if not request.user.is_superuser:
        if self.request.user.is_anonymous():
            raise PermissionDenied("You don't have authorization to view this page")
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)

class RequestUserFormMixin(object):
    """Add currently logged in user to kwargs of the current view.

    Parent class (not standalone) which modifies the get_form_kwargs() method.
    get_form_kwargs returns a dictionary of kwargs that will be passed to __init__ of a
    form. The modification provided here adds a new "user" entry to kwargs, which is the
    user submitting the HTTP request object. Example usage: to autofill the submitted_by
    field on the initial report page.
    """
    def get_form_kwargs(self):
        kwargs = super(RequestUserFormMixin, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

class LoginRequiredMixin(object):
    """Require user to be logged in to access page governed by a view which inherits from
    this mixin.

    If the current user accessing a LoginRequiredMixin page is not logged in, they will
    be redirected to a login page (which after successful login, will redirect the user
    to the originally intended destination).
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)

class NewPasswordMixin(object):
    """Require user to have changed their password before visiting the current page.

    Intercepts the current view request. If the user who created the request is logged in
    and must change their password, then they will be redirected to the password reset
    page when trying to access any view which inherits from this mixin.
    """
    def dispatch(self, request, *args, **kwargs):
        #if not request.user.is_superuser:
        if not self.request.user.is_anonymous() and self.request.user.must_change_password:
            return HttpResponseRedirect(reverse("password_change"))
        return super(NewPasswordMixin, self).dispatch(request, *args, **kwargs)

@login_required
def protected_media(request, filename):
    """View used to serve restricted media files (images uploaded to incidents)- 
    require users to be logged in to access media files.
    """
    wrapper = FileWrapper(file(settings.RESTRICTED_MEDIA_URL+filename))
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(settings.RESTRICTED_MEDIA_URL+filename)
    return response

#-----------------------------------------------------------------------------------------
# Non-Abstract Views
#-----------------------------------------------------------------------------------------
class IncidentReport(RequestUserFormMixin,NewPasswordMixin, CreateView):
    """View used to handle submission of initial event reports.
    """
    model = models.Incident
    form_class = forms.IncidentReportForm
    template_name = "incidents_nsir/incident_report_nsir.html"

    def get_initial(self):
        """Determine which form values should be initialized.

        Based on the role of the current user, initialize form values for the investigator
        and type of report (online vs. paper) accordingly.

        Returns:
            A dictionary whose keys are incident form fields and whose values depend on
            the user accessing the page.
        """
        initial = super(IncidentReport, self).get_initial()
        if self.request.user.is_anonymous():
            if settings.INVESTIGATOR_ANONYMOUS:
                initial["investigator"] = ILSUser.objects.get(username=settings.INVESTIGATOR_ANONYMOUS)
            initial["report_type"] = models.ReportType.objects.get(pk=2)
            return initial
        else:
            try:
                current_role=self.request.user.role.name
                if settings.INVESTIGATOR_ADMIN and current_role == "admin":
                    initial['investigator'] = ILSUser.objects.get(username=settings.INVESTIGATOR_ADMIN)
                elif settings.INVESTIGATOR_THERAPY and current_role == "therapist":
                    initial['investigator'] = ILSUser.objects.get(username=settings.INVESTIGATOR_THERAPY)
                elif settings.INVESTIGATOR_DOSIMETRY and current_role == "dosimetrist":
                    initial['investigator'] = ILSUser.objects.get(username=settings.INVESTIGATOR_DOSIMETRY)
                elif settings.INVESTIGATOR_PHYSICS and current_role == "physicist":
                    initial['investigator'] = ILSUser.objects.get(username=settings.INVESTIGATOR_PHYSICS)
                elif settings.INVESTIGATOR_ONCOLOGY and current_role == "physician":
                    initial['investigator'] = ILSUser.objects.get(username=settings.INVESTIGATOR_ONCOLOGY)

                if current_role == "admin" or current_role == "dosimetrist" or current_role == "physicist" or current_role == "physician":
                    initial['report_type'] = models.ReportType.objects.get(pk=2)
                else:
                    initial['report_type'] = models.ReportType.objects.get(pk=1)

                return initial
            except AttributeError:
                return initial

    def post(self, request, *args, **kwargs):
        """Explicitly include post method in case need to add future functionality.
        """
        return super(IncidentReport, self).post(self,request)

    def render_to_json_response(self,context,**response_kwargs):
        """Function which renders the report page when the request is an ajax request.

        Render the report page (template) via an ajax request. Such a request is made upon
        attempting to submit an incident report. 

        Args:
            response_kwargs: dictionary containing keys 'changed', 'incident_id', and
            'errors'. These indicate which fields changed, the unique ID, and any errors
            respectively.

        Returns:
            Returns an HttpResponse object to load the current page, while maintaining all
            currently filled fields and highlighting any errors in red. The object will 
            also indicate which fields were just changed since the previous page rendering
            and the current incident ID. 
        """
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_valid(self, form):
        """When valid form data has been POSTed: save the model instance and return an 
        HttpResponse.

        Overriding the parent method to allow for setting of additional model instance 
        field values, sending of email signals, and processing request as ajax.

        Args:
            form: Accept the current (filled) incident report form.

        Returns:
            An HttpResponse object that redirects user to the same page. If the request is
            ajax, return current filled in form. If the request is not ajax, return a
            fresh (empty) report page. Current implementation uses ajax requests.
        """
        self.get_form
        incident = form.instance

        # Assign these fields before saving the instance (ie. before calling the parent 
        # version)
        incident.flag = settings.FLAG_ALL_ON_REPORT
        incident.investigation_assigned_by = incident.submitted_by
        incident.investigation_assigned_date = incident.submitted
        incident.date_last_reminder = incident.submitted

        # Assign an Incident ID for online reports
        if incident.report_type.pk == 2:
            incident.incident_id = self.get_next_online_id()

        # Set NSIR number_patients_affected field
        if incident.event_type.pk == 1:
            incident.number_patients_involved = 0
            incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=1)
        elif incident.event_type.pk == 2:
            incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=1)
        elif incident.event_type.pk == 3:
            if incident.number_patients_involved == 1:
                incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=2)
            else:
                incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=3)

        # Set local severity levels
        if incident.event_type.pk == 1:
            incident.local_severity_level_id = 1
        elif incident.event_type.pk == 2:
            incident.local_severity_level_id = 2

        # Call the parent version, which includes saving the instance
        response = super(IncidentReport, self).form_valid(form)

        user = form.cleaned_data["submitted_by"]
        incident.investigation.assigned_by = incident.submitted_by

        # Send email notifications
        signals.investigator_assigned.send(sender=self, incident=incident)
        signals.oncologist_submitted.send(sender=self, incident=incident)
        if self.request.user.is_anonymous():
            signals.notify_managers.send(sender=self, incident=incident)

        if self.request.is_ajax():
            return self.render_to_json_response({'changed':form.changed_data,'incident_id':incident.incident_id,'errors':None})
        else:
            return response

    def form_invalid(self, form):
        """When invalid form data has been POSTed: render the report page while
        maintaining current field values and display errors in meaningful way.

        Overriding the parent method to allow for processing request as ajax.

        Args:
            form: Accept the current (filled) incident report form.

        Returns:
            An HttpResponse object that redirects user to the same page. If the request is
            ajax, return current filled in form. If the request is not ajax, return a
            fresh (empty) report page. Current implementation uses ajax requests.
        """
        response = super(IncidentReport,self).form_invalid(form)

        if self.request.is_ajax():
            return self.render_to_json_response({'changed':None,'incident_id':None,'errors':form.errors})
        else:
            return response

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Overriding the parent method to supply a dictionary of help texts that should be
        used in the tooltips that are displayed for FK fields. Also generate the next
        online ID to assign.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
        """
        context = super(IncidentReport, self).get_context_data(*args, **kwargs)
        context["base_template"] = BASE_TEMPLATE

        # Establish a dictionary for all incident model FK fields which appear in the
        # report form, with each key corresponding to an array of all instances (options)
        # associated with that model. This is needed in generating the tooltips which
        # describe what each option is from the dropdown menus.
        help_dictionary = {
            'id_report_type': models.ReportType.objects.all(),
            'id_event_type': models.EventType.objects.all(),
            #'acute_medical_harm': models.AcuteMedicalHarm.objects.all(),
            #'id_oncologist': models.Oncologist.objects.all(),
            'id_diagnosis': models.Diagnosis.objects.all(),
            'id_functional_work_area': models.FunctionalWorkArea.objects.all(),
            #'time_period_occurred': models.TimePeriodOccurred.objects.all(),
            'id_time_period_detected': models.TimePeriodDetected.objects.all(),
            # 'id_number_patients_affected': models.NumberPatientsAffected.objects.all(),
            'id_support_required': models.SupportRequired.objects.all(),
            'id_support_given': models.SupportGiven.objects.all(),
            'id_patient_support_required': models.SupportRequired.objects.all(),
            'id_patient_support_given': models.SupportGiven.objects.all(),
            'id_investigator': ILSUser.objects.filter(is_investigator=True),
            'id_oncologist': ILSUser.objects.filter(is_oncologist=True),
        }
        context["help_dictionary"] = help_dictionary

        return context

    def get_next_online_id(self):
        """Determine and return the next ID number (incident_id) to be assigned to a new 
        online incident.

        Returns:
            An integer representing the ID number that can be safely assigned to a new 
            incident reported using an online report.
        """
        # Determine the largest ID associated with an online report currently in the DB
        max_online_id = models.Incident.objects.filter(
            Q(incident_id__gte=MIN_ONLINE_ID),
            Q(incident_id__lte=MAX_ONLINE_ID),
            Q(report_type=2)
        ).aggregate(Max('incident_id'))['incident_id__max']

        # Handle case for first online incident report submitted
        next_online_id = None
        if max_online_id:
            next_online_id = max_online_id + 1
        else:
            next_online_id = MIN_ONLINE_ID

        # Get all the ID numbers in the DB that are equal to or larger than the above
        # determined next_online_id. This is required for the case whereby paper
        # reports are submitted with manually entered ID numbers within the range
        # set aside for online incident reports. Continue incrementing the online
        # ID until it is unique
        larger_ids = models.Incident.objects.filter(incident_id__gte=next_online_id).values_list('incident_id',flat=True)
        while next_online_id in larger_ids:
            next_online_id = next_online_id + 1

        return next_online_id


class ChangeEventType(StaffRequiredMixin,NewPasswordMixin, LoginRequiredMixin, DetailView):
    """View used to change the event type of a previously reported incident.

    This separate view is required (beyond allowing simple change in the investigation view)
    because of the difference in forms used for each event type (see forms.py). Thus, changing
    the event type requires a complete page refresh, not ajax. Also, additional fields that
    would have been entered in the initial report are required if going from RC to NM or actual
    incident. These are provided in this view. The view also handles updating the completion
    status based on the changes made, as well as deleting values previously saved if those
    fields no longer apply to the new event type (e.g. going from ACT to RC). Only the
    investigator and admins are allowed access to this page.
    """
    model = models.Incident
    template_name = "incidents_nsir/change_event_type.html"

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Overriding the parent method to supply a dictionary of help texts that should be
        used in the tooltips that are displayed for FK fields. Also generate the next
        online ID to assign.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
        """
        context = super(ChangeEventType, self).get_context_data(*args, **kwargs)

        incident = self.object

        context["incident"] = incident

        #Must pass the form name (pass as hidden input in the template)
        posting_form = self.request.POST.get("form_name")
        if posting_form == "change_event_type_form":
            context["form"] = forms.ChangeEventTypeForm(self.request.POST, instance=incident)
        else:
            context["form"] = forms.ChangeEventTypeForm(instance=incident)            

        # Establish a dictionary for all relevant incident model FK fields which appear in the
        # form, with each key corresponding to an array of all instances (options)
        # associated with that model. This is needed in generating the tooltips which
        # describe what each option is from the dropdown menus.
        help_dictionary = {
            'id_event_type': models.EventType.objects.all(),
            'id_diagnosis': models.Diagnosis.objects.all(),
            'id_oncologist': ILSUser.objects.filter(is_oncologist=True),
            # 'id_number_patients_affected': models.NumberPatientsAffected.objects.all(),
        }
        context["help_dictionary"] = help_dictionary

        # Get the next page (i.e. to redirect to investigation page)
        context["next"] = self.request.GET.get("next", None)

        return context

    def post(self, request, *args, **kwargs):
        """Handle post of form data, determine validity, and handle appropriately.
        """
        self.object = self.model.objects.get(incident_id=self.kwargs['incident_id'])
        context = self.get_context_data(**kwargs)
        form = context["form"]

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def render_to_json_response(self,context,**response_kwargs):
        """Used to render an ajax response (i.e. if form invalid).
        """
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def get_success_url(self, same_type):
        """Define the URL to be accessed upon successfully changing event type, and pass
        message to the new page.
        """
        if same_type:
            messages.warning(self.request, "No change to Event Type")
        else:
            messages.success(self.request, "Successfully changed Event Type to %s" % (self.object.event_type))

        #Should always redirect to investigation page. Other options are error backups.
        if self.request.POST.get("next", None) == "incident":
            return reverse("incidents_nsir:incident", kwargs={"incident_id":self.kwargs['incident_id']}) + "#impact"
        elif self.request.user.is_investigator:
            return reverse("incidents_nsir:dashboard")

        return reverse("incidents_nsir:search")

    def form_valid(self, form):
        """When valid form data has been POSTed: Process changes made, save the model
        instance, send email notifications, and return an HttpResponse.

        Overriding the parent method to allow for setting of additional model instance 
        field values, sending of email signals, and processing request as ajax.

        Args:
            form: Accept the current (filled) incident report form.

        Returns:
            An HttpResponse object that redirects user to the page determined in the
            get_success_url method.
        """
        updated_incident = form.save(commit=False)
        form.save_m2m()
        inc_id = self.object.incident_id

        # Set NSIR number_patients_affected field
        if updated_incident.event_type.pk == 1:
            updated_incident.number_patients_involved = 0
            updated_incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=1)
        elif updated_incident.event_type.pk == 2:
            updated_incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=1)
        elif updated_incident.event_type.pk == 3:
            if updated_incident.number_patients_involved == 1:
                updated_incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=2)
            else:
                updated_incident.number_patients_affected = models.NumberPatientsAffected.objects.get(pk=3)

        # Get incident parameters before new changes are applied (for upcoming logic)
        old_incident = models.Incident.objects.get(incident_id=inc_id)
        old_type = old_incident.event_type
        old_complete = old_incident.investigation_complete

        # Set local severity levels
        if updated_incident.event_type.pk == 1:
            updated_incident.local_severity_level_id = 1
        elif updated_incident.event_type.pk == 2:
            updated_incident.local_severity_level_id = 2
        elif updated_incident.event_type.pk == 3:
            # If was not previously an actual incident, but now is; remove entry for local_severity_level
            if old_incident.event_type.pk != 3:
                updated_incident.local_severity_level = None


        # Delete previous field values as necessary depending on new/old event type
        unfilled_incident = self.unfill_fields(updated_incident, old_type)

        # Adjust completion status as necessary
        ready_incident = self.adjust_completion(unfilled_incident, old_complete)

        # Send oncologist email notification if newly assigned oncologist
        if old_incident.oncologist != updated_incident.oncologist:
            signals.oncologist_submitted.send(sender=self, incident=ready_incident)            

        ready_incident.save()

        same_type = ready_incident.event_type == old_type

        return HttpResponseRedirect(self.get_success_url(same_type))

    def form_invalid(self, form):
        """When invalid form data has been POSTed: render the report page while
        maintaining current field values and display errors in meaningful way.

        Overriding the parent method to allow for processing request as ajax.

        Args:
            form: Accept the current (filled) incident report form.

        Returns:
            An HttpResponse object that redirects user to the same page. If the request is
            ajax, return current filled in form. If the request is not ajax, return a
            fresh (empty) report page. Current implementation uses ajax requests.
        """

        if self.request.is_ajax():
            return self.render_to_json_response({'errors':form.errors})
        else:
            return response

    def unfill_fields(self, incident, old_type):
        """Delete previously filled field values conditionally based on the previous and
        newly defined event types.

        Returns:
            The updated incident (with appropriate fields deleted) object. NOTE: the incident
            has not yet been saved.
        """
        new_type = incident.event_type

        # Determine which fields should be deleted
        # old_ and new_fields store field values which are not shared among all event types
        # specifically for the old and new event type
        old_fields = models.Incident.get_uncommon_fields(old_type.id)
        new_fields = models.Incident.get_uncommon_fields(new_type.id)
        delete_fields = []
        for ofield in old_fields:
            if ofield not in new_fields:
                delete_fields.append(ofield)

        # Delete the pertinent existing field values according to the type of field
        # i.e. deletion process differs for CharFields, FKs, and M2Ms
        for field in delete_fields:
            field_type = incident._meta.get_field(field).get_internal_type()
            if field_type == "CharField":
                setattr(incident,field,"")
            elif field_type == "ForeignKey" or field_type == "DecimalField" or field_type == "PositiveIntegerField":
                setattr(incident,field,None)
            elif field_type == "ManyToManyField":
                many_manager = getattr(incident,field)
                many_manager.clear()

        return incident

    def adjust_completion(self, incident, old_complete):
        """Adjust the completion status of the updated incident if required.

        Returns:
            The updated incident (with updated completion status) object. NOTE: teh incident
            has not yet been saved.
        """
        now_complete = None
        if incident.is_complete():
            now_complete = True
        else:
            now_complete = False

        # If was completed, and now is not
        if old_complete and not now_complete:
            incident.investigation_complete = False
            incident.investigation_completed_date = None
        # If completed now, but wasn't previously
        elif now_complete and not old_complete:
            incident.investigation_complete = True
            incident.investigation_completed_date = timezone.now()
            signals.incident_completed.send(sender=self, incident=incident)

        return incident

    def dispatch(self, request, *args, **kwargs):
        """Method called when attempting to generate the view, prevents users without
        appropriate credentials from accessing.

        Only the current user and admin users can access the investigation page.
        """
        incident = self.get_object()
        if not (self.request.user == incident.investigator or self.request.user.is_superuser):
            raise PermissionDenied("You don't have authorization to view this page")
        return super(ChangeEventType, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        return models.Incident.objects.get(incident_id=self.kwargs.get("incident_id"))

class IncidentInvestigation(StaffRequiredMixin,NewPasswordMixin, LoginRequiredMixin, DetailView):
    """View used to handle the investigation form for a parituclar incident instance.
    """
    model = models.Incident
    template_name = "incidents_nsir/investigation_nsir.html"

    def post(self, request, *args, **kwargs):
        """Explicitly include post method in order to handle multiple types of forms (i.e. 
        a formset) when POSTing data to the page.

        The form_name is determined from the POSTed request, and an appropriate context
        according to the form type is established.
        """
        self.object = self.model.objects.get(incident_id=self.kwargs['incident_id'])
        context = self.get_context_data(**kwargs)
        context["incident"] = self.object # current incident object

        dispatch = {
            "investigation_form": self.handle_investigation_form,
            "invalid_form": self.handle_invalid_form,
            "valid_form": self.handle_valid_form,
            "action_create_form": self.handle_action_create_form,
            "action_update_formset": self.handle_action_update_form,
        }

        return dispatch[self.request.POST.get("form_name")](context)

        # dispatch_key = self.request.POST.get("form_name")

        # if any(char.isdigit() for char in dispatch_key):
        #     results = re.findall('\d+|\D+', dispatch_key)
        #     dispatch_key = results[0][:-1]
        #     form_id = results[1]
        #     return dispatch[dispatch_key](context,form_id)
        # else:
        #     return dispatch[dispatch_key](context)

    def get_queryset(self):
        """Returns a queryset (set of incidents) that will be used to retrieve the
        incident that this view will display.

        A queryset represents a collection of objects from the DB (can be filtered).
        Override existing method to allow for changes to that queryset; but currently
        unused.
        """
        return super(IncidentInvestigation, self).get_queryset()

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Overriding the parent method to supply a dictionary of help texts that should be
        used in the tooltips that are displayed for FK fields. Also pass the correct
        form instance (of the correct type, either for a RC, NM, or actual incident).
        Need to identify the current user as well, so that subscription information can be
        displayed properly.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
        """
        context = super(IncidentInvestigation, self).get_context_data(*args, **kwargs)
        incident = self.object

        context["incident"] = incident
        context["date_occurred"] = incident.date_incident_occurred

        # Determine which form on the investigation page is being POSTed to. The actual
        # investigation form, the invalid form, valid form, or action create/update forms.
        # The form which is being POSTed to takes the request POST data, the other forms
        # are simply bound to the instance in the DB for determining context.
        to_handle = self.request.POST.get("form_name")
        event_type_id = incident.event_type.pk

        investigator_key = self.request.POST.get("investigator")
        if not investigator_key:
            investigator_key = incident.investigator.pk
        if to_handle == "investigation_form":
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(self.request.POST, instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(self.request.POST, instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(self.request.POST, instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(instance=incident)
            context["valid_form"] = forms.ValidForm(instance=incident)
            context["action_create_form"] = forms.ActionCreateForm()
            context["action_update_formset"] = forms.IncidentActionFormSet(queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))
        elif to_handle == "invalid_form":
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(self.request.POST, instance=incident)
            context["valid_form"] = forms.ValidForm(instance=incident)
            context["action_create_form"] = forms.ActionCreateForm()
            context["action_update_formset"] = forms.IncidentActionFormSet(queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))
        elif to_handle == "valid_form":
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(instance=incident)
            context["valid_form"] = forms.ValidForm(self.request.POST, instance=incident)
            context["action_create_form"] = forms.ActionCreateForm()
            context["action_update_formset"] = forms.IncidentActionFormSet(queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))
        elif to_handle == "action_create_form":
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(instance=incident)
            context["valid_form"] = forms.ValidForm(instance=incident)
            context["action_create_form"] = forms.ActionCreateForm(self.request.POST)
            context["action_update_formset"] = forms.IncidentActionFormSet(queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))
        elif to_handle == "action_update_formset":
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(instance=incident)
            context["valid_form"] = forms.ValidForm(instance=incident)
            context["action_create_form"] = forms.ActionCreateForm()
            context["action_update_formset"] = forms.IncidentActionFormSet(self.request.POST, queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))
        else:
            if event_type_id == 1:
                context["investigation_form"] = forms.InvestigationRCForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            elif event_type_id == 2:
                context["investigation_form"] = forms.InvestigationNMForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            else:
                context["investigation_form"] = forms.InvestigationForm(instance=incident, user=self.request.user, investigator_key=investigator_key)
            context["invalid_form"] = forms.InvalidForm(instance=incident)
            context["valid_form"] = forms.ValidForm(instance=incident)
            context["action_create_form"] = forms.ActionCreateForm()
            context["action_update_formset"] = forms.IncidentActionFormSet(queryset=models.IncidentAction.objects.filter(incident=incident).order_by('-date_assigned'))

        context['model'] = models.Incident
        context["subscription"] = incident.subscription.filter(user=self.request.user).count() > 0

        # Establish a dictionary for all incident model FK fields which appear in the
        # investigation form, with each key corresponding to an array of all instances
        # (options) associated with that model. This is needed in generating the tooltips
        # which describe what each option is from the dropdown menus.
        help_dictionary = {
            'id_report_type': models.ReportType.objects.all(),
            'id_submitted_by': ILSUser.objects.all(),
            'id_oncologist': ILSUser.objects.filter(is_oncologist=True),
            'id_event_type': models.EventType.objects.all(),
            # 'id_acute_medical_harm': models.AcuteMedicalHarm.objects.all(),
            'id_local_severity_level': models.LocalSeverityLevel.objects.filter(pk__gte=3),
            'id_dosimetric_impact': models.DosimetricImpact.objects.all(),
            'id_latent_medical_harm': models.LatentMedicalHarm.objects.all(),
            'id_functional_work_area': models.FunctionalWorkArea.objects.all(),
            'id_time_period_occurred': models.TimePeriodOccurred.objects.all(),
            'id_time_period_detected': models.TimePeriodDetected.objects.all(),
            'id_patient_month_birth': models.Month.objects.all(),
            'id_patient_gender': models.PatientGender.objects.all(),
            'id_diagnosis': models.Diagnosis.objects.all(),
            'id_process_step_occurred': models.ProcessStepOccurred.objects.all(),
            'id_process_step_detected': models.ProcessStepDetected.objects.all(),
            'id_problem_type': models.ProblemType.objects.all(),
            # 'id_number_patients_affected': models.NumberPatientsAffected.objects.all(),
            'id_radiation_treatment_techniques': models.RadiationTreatmentTechnique.objects.all(),
            'id_treatment_intent': models.TreatmentIntent.objects.all(),
            'id_support_required': models.SupportRequired.objects.all(),
            'id_support_given': models.SupportGiven.objects.all(),
            'id_patient_support_required': models.SupportRequired.objects.all(),
            'id_patient_support_given': models.SupportGiven.objects.all(),
            'id_investigator': ILSUser.objects.filter(is_investigator=True),
            'id_responsible': ILSUser.objects.filter(is_investigator=True),
            'id_predefined_type': models.PredefinedIncident.objects.all(),
        }
        context["help_dictionary"] = help_dictionary

        context["can_edit"] = self.request.user.can_edit(investigator_pk=incident.investigator.pk)
        
        context["missing_field_ids"] = incident.get_missing_field_ids()

        context["missing_field_verbose_names"] = incident.get_missing_field_verbose_names()

        context["NA_fields"] = incident.get_NA_field_ids()

        # The following context items are used for highlighting fields that are conditionally
        # mandatory depending on a threshold value for acute medical harm
        context["local_mandatory_field_ids"] = incident.get_local_mandatory_field_ids()

        context["local_mandatory_field_names"] = incident.get_local_mandatory_field_verbose_names()

        context["local_mandatory_fields_html"] = incident.get_local_mandatory_field_html_ids()

        context["acute_medical_harm_threshold"] = incident.get_acute_medical_harm_threshold()

        context["local_mandatory_dicts"] = incident.get_local_mandatory_field_dicts()

        # context["template_fields"] = json.dumps(models.AllowedTemplateField.objects.filter(event_type=incident.event_type).values_list('field_name'), cls=DjangoJSONEncoder)
        context["template_fields"] = json.dumps(list(models.AllowedTemplateField.objects.filter(event_type__name=incident.event_type).values_list('field_name', flat=True)), cls=DjangoJSONEncoder)

        context["template_form"] = forms.TemplateForm()

        context["incidentimage_form"] = forms.IncidentImageForm()

        return context

    def get_next_url(self):
        """Method to determine which URL to redirect to, determined upon page load (get or
        post).

        Access parameters of the GET request to determine what the next URL to be accessed
        is. If the request is a save-and-continue, go to the next investigation in the
        queue. Current implmentation (following ajax posts as well), always supplies the
        currernt page as the next URL

        Returns:
            A string representing the next URL to be accessed. (e.g. /nsir/incident/100)
        """
        default = reverse("incidents_nsir:incident", kwargs={"incident_id": self.object.incident_id})

        next_ = self.request.GET.get("next", default)
        next_ = re.sub("^(.*)data\/?$", "\g<1>", next_)
        next_from = self.request.GET.get("continue", None)

        if self.request.POST.get("save_and_continue", "0") != "0":
            try:
                incident_id = getattr(models.Incident, next_from).exclude(incident_id=self.object.incident_id).values("incident_id").latest("incident_id")['incident_id']
                next_ = "%s?next=%s&continue=%s" % (reverse("incident", kwargs={"incident_id": incident_id}), next_, next_from)
            except (AttributeError, TypeError, models.Incident.DoesNotExist):
                pass

        return next_

    def render_to_json_response(self,context,**response_kwargs):
        """Function which renders the report page when the request is an ajax request.

        Render the report page (template) via an ajax request. Such a request is made upon
        attempting to submit an incident report. 

        Args:
            response_kwargs: dictionary containing keys 'changed', 'incident_id', and
            'errors'. These indicate which fields changed, the unique ID, and any errors
            respectively.

        Returns:
            Returns an HttpResponse object to load the current page, while maintaining all
            currently filled fields and highlighting any errors in red. The object will 
            also indicate which fields were just changed since the previous page rendering
            and the current incident ID. 
        """
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def handle_action_update_form(self, context):
        """Process updates (POSTs) to the action formset form, containing one or more 
        forms.

        Handles the posting of data to the actions formset. Accounts uniquely for actions
        which were added to the formset after the initial page load (i.e were added via
        AJAX POSTs). Creates dictionary of JSON data for jQuery to allow user to visualize
        erroneous/successful changes made to the forms in the formset.

        Returns:
            An HttpResponse object representing the next page to be loaded. Currently
            returning an ajax relaod of the same page, but highlighting changes made
            to the action forms.
        """
        formset = context["action_update_formset"]

        # If there are no errors in any of the forms in the formset:
        if formset.is_valid():
            # If unauthorized user somehow attempts to update the form:
            if self.request.user.is_anonymous():
                django_messages.append(messages.error(self.request, "Error updating Incident. You don't have the required permissions."))
                response_data['messages'] = django_messages
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # response_data dictionary will hold the data to be provided as JSON data to 
            # jQuery functions
            response_data = {}
            response_data['num_forms'] = formset.total_form_count()
            response_data['errors'] = None

            # Arrays to hold response data from each of the action forms in the formset.
            # Will add these to response_data dictionary after processing each form
            just_completed = []
            just_incompleted = []
            array_completed_date = []
            array_completed_by = []
            formset_changed = []

            was_changed = False

            # Loop through each action form:
            for form in formset:
                # If the form was changed:
                if len(form.changed_data) > 0:
                    updated_action = form.save(commit=False)

                    new_action = False

                    # Handle newly added actions to the formset:
                    try:
                        updated_action.incident
                    except ObjectDoesNotExist:
                        # b/c newly added forms are not bound to an instance in the DB,
                        # will always look like data has changed compared to initial. So
                        # need to determine which fields actually changed manually, for
                        # new instances
                        new_form_changes = []

                        new_action = True

                        # Get the existing action (which was saved upon creating the new
                        # action) using a modelform field which is not bound to an action
                        # instance.
                        query_id = form.clean()['instance_id']
                        existing_action = models.IncidentAction.objects.get(id=query_id)

                        # the action was just completed
                        if existing_action.complete != updated_action.complete and updated_action.complete:
                            just_completed.append(True)
                            just_incompleted.append(False)
                            existing_action.complete = updated_action.complete
                            existing_action.completed_by = self.request.user
                            existing_action.date_completed = timezone.now()
                            existing_action.description_performed = updated_action.description_performed
                            new_form_changes.append('complete')
                            new_form_changes.append('description_performed')
                            was_changed = True
                        # the action was just incompleted
                        elif existing_action.complete != updated_action.complete and not updated_action.complete:
                            just_completed.append(False)
                            just_incompleted.append(True)
                            existing_action.complete = updated_action.complete
                            existing_action.completed_by = None
                            existing_action.date_completed = None
                            existing_action.description_performed = ""
                            new_form_changes.append('complete')
                            new_form_changes.append('description_performed')
                            was_changed = True
                        #complete status did not change
                        else: 
                            just_completed.append(False)
                            just_incompleted.append(False)
                            if existing_action.description_performed != updated_action.description_performed:
                                existing_action.description_performed = updated_action.description_performed
                                new_form_changes.append('description_performed')
                                was_changed = True

                        updated_action = existing_action
                        existing_action.save()
                        formset_changed.append(new_form_changes)

                    # Hanlde existing forms in the formset:
                    if not new_action:
                        # Handle updating completion info
                        if "complete" in form.changed_data:
                            # the action was just completed
                            if updated_action.complete:
                                updated_action.completed_by = self.request.user
                                updated_action.date_completed = timezone.now()
                                just_completed.append(True)
                                just_incompleted.append(False)
                            # the action was just incompleted
                            else:
                                updated_action.completed_by = None
                                updated_action.date_completed = None
                                just_completed.append(False)
                                just_incompleted.append(True)
                        # complete status did not change
                        else:
                            just_completed.append(False)
                            just_incompleted.append(False)
                        formset_changed.append(form.changed_data)
                        was_changed = True

                    # Handle date completed
                    string_date_completed = ""
                    if updated_action.date_completed:
                        local_dt = updated_action.date_completed + datetime.timedelta(hours=-5) # Would like to fix this, hardcoding timezone conversion
                        # '-' removes leading zero
                        string_date_completed = strftime("%B %-d, %Y, %-I:%M %p", local_dt.timetuple()) # Format date string passed to jquery as Django displays dates
                    array_completed_date.append(string_date_completed)

                    # Handle completed by
                    if updated_action.completed_by:
                        array_completed_by.append(str(updated_action.completed_by))
                    else:
                        array_completed_by.append("")
                    
                    updated_action.save()

                    if just_completed[-1]:
                        signals.action_completed.send(sender=self, action=updated_action, incident=updated_action.incident)

                # The form was not changed - no changes to the instance bound to the
                # action form. Just append reponse data accordingly.
                else:
                    array_completed_date.append("")
                    array_completed_by.append("")
                    just_completed.append(False)
                    just_incompleted.append(False)
                    formset_changed.append(form.changed_data)

            #************************************************************************************
            # Incident completion status is dependent on whether or not there are any outstanding
            # actions to be completed. Thus, update the incident accordingly using the was_changed
            # variable that is set to True if any changes were made to any of the actions. Also
            # send relevant info as JSON response data. Similar to behaviour in the
            # handle_investigation_form() method defined below
            inc_just_completed = False
            inc_just_incompleted = False
            if was_changed:
                updated_incident = self.object

                old_complete = updated_incident.investigation_complete
                old_complete_date = updated_incident.investigation_completed_date

                # Determine if there are missing fields in the investigation which are
                # required for NSIR-RT sharing
                required_complete = updated_incident.is_complete()
                updated_incident.investigation_complete = required_complete

                # If the investigation was just completed upon most recent POST, update the
                # datetime in the DB
                inc_just_completed = updated_incident.investigation_complete and not old_complete
                if inc_just_completed and old_complete_date == None:
                    updated_incident.investigation_completed_date = timezone.now()

                # Remove completed date if a previously-completed incident was updated so that
                # it is no longer complete.
                if not required_complete:
                    if updated_incident.investigation_completed_date:
                        inc_just_incompleted = True
                    updated_incident.investigation_completed_date = None

                # Only send completed investigation email to subscribers if the investigation
                # was not complete prior to the most recent POST
                if inc_just_completed:
                    signals.incident_completed.send(sender=self, incident=updated_incident)

                updated_incident.save()

                # JSON response data to be used for highlighting missing fields on the 
                # investigation page (orange highlighting currently)
                response_data['field_labels'] = updated_incident.get_field_ids()
                response_data['missing_fields'] = updated_incident.get_missing_field_verbose_names()
                response_data['missing_field_labels'] = updated_incident.get_missing_field_ids()
                
                # If the investigation is complete, instead of displaying a list of missing
                # fields, should display the date of completion.
                response_data['inv_complete'] = updated_incident.investigation_complete
                if (response_data['inv_complete']):
                    response_data['inv_complete_date'] = updated_incident.investigation_completed_date.strftime('%B %-d, %Y, %I:%M %p')
                    response_data['inv_narrative'] = updated_incident.investigation_narrative
                    response_data['inv_narrative_by'] = updated_incident.narrative_by.get_name()
                    response_data['investigator'] = updated_incident.investigator.get_name()

                # Indicate to JSON if the investigation has just been completed or was
                # complete, but now is not.
                response_data['inc_just_completed'] = inc_just_completed
                response_data['inc_just_incompleted'] = inc_just_incompleted

                # Indicate to JSON if the incident is marked as valid for trending
                response_data['valid'] = updated_incident.valid
                response_data['invalid_reason'] = updated_incident.invalid_reason
                if updated_incident.valid_status_by != None and updated_incident.valid_status_by != "":
                    response_data['valid_status_by'] = updated_incident.valid_status_by.get_name()
                else:
                    response_data['valid_status_by'] = ""

                response_data['can_edit'] = self.request.user.can_edit(investigator_pk=updated_incident.investigator.pk)

            #************************************************************************************

            response_data['just_completed'] = just_completed
            response_data['just_incompleted'] = just_incompleted
            response_data['completed_date'] = array_completed_date
            response_data['completed_by'] = array_completed_by
            response_data['changed'] = formset_changed

            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
        
        # There were errors in at least one form in the formset
        else:
            response_data = {}
            response_data['num_forms'] = formset.total_form_count()
            response_data['errors'] = formset.errors

            return self.render_to_json_response(response_data)       

    def handle_action_create_form(self, context):
        """Process POST data when creating a new IncidentAction object.

        Returns:
            An HttpResponse object representing the next page to be loaded. Currently
            returning an ajax relaod of the same page, but highlighting errors/success
            in creating the new object.
        """
        form = context['action_create_form']

        # Creation form was valid:
        if form.is_valid():
            # Throw error if anonymous user somehow made it to investigation page:
            if self.request.user.is_anonymous():
                django_messages.append(messages.error(self.request, "Error updating Incident. You don't have the required permissions."))
                response_data['messages'] = django_messages
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            new_action = form.save(commit=False)
            new_action.incident = self.object

            # Determine what the next online ID is by querying existing incidents
            next_action_id = models.IncidentAction.objects.filter(
                incident=new_action.incident
            ).aggregate(Max('action_id'))['action_id__max']
            if next_action_id:
                next_action_id = next_action_id + 1
            else:
                next_action_id = 1
            new_action.action_id = next_action_id

            # Establish the current user and date/time
            new_action.assigned_by = self.request.user
            new_action.date_assigned = timezone.now()
            new_action.date_last_reminder = new_action.date_assigned
            new_action.save()

            #************************************************************************************
            # Incident completion status is dependent on whether or not there are any outstanding
            # actions to be completed. Thus, the incident is no longer complete (if it was before)
            # after creating a new action.
            updated_incident = new_action.incident
            old_complete = updated_incident.investigation_complete
            updated_incident.investigation_complete = False
            updated_incident.investigation_completed_date = None
            updated_incident.save()
            #************************************************************************************

            # response_data dictionary to be supplied to jQuery as JSON
            response_data = {}
            # Need the following to link a newly created ActionUpdateForm in the formset
            # to this created Action (in case updates are performed), b/c that new
            # ActionUpdateForm is generated dynamically and is not actually bound to the
            # instance created here
            response_data['id_pk'] = new_action.id
            response_data['responsible_first'] = new_action.responsible.first_name
            response_data['responsible_last'] = new_action.responsible.last_name
            response_data['incident_id'] = new_action.incident.incident_id
            response_data['action_id'] = new_action.action_id
            response_data['description_proposed'] = new_action.description_proposed
            response_data['responsible'] = str(new_action.responsible)
            response_data['assigned_by'] = str(new_action.assigned_by)

            # Formatting date for JSON
            local_dt = new_action.date_assigned + datetime.timedelta(hours=-5)
            # '-' removes leading zero
            string_date_assigned = strftime("%B %-d, %Y, %-I:%M %p", local_dt.timetuple())
            response_data['date_assigned'] = string_date_assigned

            signals.action_assigned.send(sender=self, action=new_action, incident=new_action.incident)
            #signals.incident_invalid.send(sender=self, incident=updated_incident, invalid_reason=updated_incident.invalid_reason)
            #signals.investigator_assigned.send(sender=self, incident=updated_incident)
            #signals.investigator_unassigned.send(sender=self, incident=updated_incident, old_investigator=prev_investigator)

            #************************************************************************************
            # Handle passing of JSON data to accurately display incident investigation completion
            # status (no longer complete)

            # JSON response data to be used for highlighting missing fields on the 
            # investigation page (orange highlighting currently)
            response_data['field_labels'] = updated_incident.get_field_ids()
            response_data['missing_fields'] = updated_incident.get_missing_field_verbose_names()
            response_data['missing_field_labels'] = updated_incident.get_missing_field_ids()
            
            # If the investigation is complete, instead of displaying a list of missing
            # fields, should display the date of completion.
            response_data['inv_complete'] = updated_incident.investigation_complete

            # Indicate to JSON if the investigation has just been completed or was
            # complete, but now is not.
            response_data['just_completed'] = False
            response_data['just_incompleted'] = old_complete

            # Indicate to JSON if the incident is marked as valid for trending
            response_data['valid'] = updated_incident.valid
            response_data['invalid_reason'] = updated_incident.invalid_reason
            if updated_incident.valid_status_by != None and updated_incident.valid_status_by != "":
                response_data['valid_status_by'] = updated_incident.valid_status_by.get_name()
            else:
                response_data['valid_status_by'] = ""

            response_data['can_edit'] = self.request.user.can_edit(investigator_pk=updated_incident.investigator.pk)
            #************************************************************************************

            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

        #Creation form was invalid:
        else:
            return self.render_to_json_response({'errors':form.errors})

    def handle_invalid_form(self, context):
        """Process updates (POSTs) to the form which allows users to mark an incident as
        invalid for trending.

        Handles posting of data to the invalidation form. If the form does not contain
        errors, set the incident as invalid and apply the user's inputted reasoning. Save
        the user who set this, as well as the current date. Send an email to subscribed
        users. Handle json data for determining missing fields in order to preserve
        feature of displaying missing fields if the investigation were to be re-opened.
        NOTE THIS IS NOT USED TO HANDLE ERRONEOUS (INVALID) FORM DATA!

        Returns:
            An HttpResponse object representing the next page to be loaded. Currently
            returning an ajax relaod of the same page, but changing the valid status and
            coloring appropriately.
        """
        form = context['invalid_form']

        if form.is_valid():
            # Throw error if anonymous user somehow made it to investigation page:
            if self.request.user.is_anonymous():
                django_messages.append(messages.error(self.request, "Error updating Incident. You don't have the required permissions."))
                response_data['messages'] = django_messages
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            updated_incident = form.save()
            updated_incident.valid = False
            updated_incident.valid_status_date = timezone.now()
            updated_incident.valid_status_by = self.request.user
            updated_incident.save()

            signals.incident_invalid.send(sender=self, incident=updated_incident, invalid_reason=updated_incident.invalid_reason)

            response_data = {}

            # JSON response data to be used for highlighting missing fields on the 
            # investigation page (orange highlighting currently)
            response_data['field_labels'] = updated_incident.get_field_ids()
            response_data['missing_fields'] = updated_incident.get_missing_field_verbose_names()
            response_data['missing_field_labels'] = updated_incident.get_missing_field_ids()
            
            # If the investigation is complete, instead of displaying a list of missing
            # fields, should display the date of completion.
            response_data['inv_complete'] = form.instance.investigation_complete

            # Indicate to JSON if the investigation has just been completed or was
            # complete, but now is not.
            response_data['just_completed'] = False
            response_data['just_incompleted'] = False

            # Indicate to JSON if the incident is marked as valid for trending
            response_data['valid'] = form.instance.valid
            response_data['invalid_reason'] = form.instance.invalid_reason
            response_data['valid_status_by'] = form.instance.valid_status_by.get_name()
            response_data['valid_status_date'] = form.instance.valid_status_date.strftime('%B %-d, %Y, %I:%M %p')

            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

            # return HttpResponseRedirect(self.get_next_url())
        else:
            return self.render_to_json_response({'errors':form.errors})
            #return HttpResponseRedirect(self.get_next_url())

    def handle_valid_form(self, context):
        """Process updates (POSTs) to the form which allows users to re-open an
        investigation for an incident flagged as invalid for trending.

        Handles posting of data to the validation form. This form is hidden and contains
        no user-inputted fields. A simple button press will initiate this process. Save
        the user who set this, as well as the current date. Send an email to subscribed
        users. Handle json data for determining missing fields in order to preserve
        feature of displaying missing fields if the investigation were to be re-opened.
        NOTE THIS IS NOT USED TO HANDLE PROPER (VALID) FORM DATA!

        Returns:
            An HttpResponse object representing the next page to be loaded. Currently
            returning an ajax relaod of the same page, but changing the valid status and
            coloring appropriately.
        """
        form = context['valid_form']

        if form.is_valid():
            # Throw error if anonymous user somehow made it to investigation page:
            if self.request.user.is_anonymous():
                django_messages.append(messages.error(self.request, "Error updating Incident. You don't have the required permissions."))
                response_data['messages'] = django_messages
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            updated_incident = form.save()
            updated_incident.valid = True
            updated_incident.invalid_reason = None
            updated_incident.valid_status_date = timezone.now()
            updated_incident.valid_status_by = self.request.user
            updated_incident.save()

            signals.incident_reopened.send(sender=self, incident=updated_incident)

            response_data = {}

            # JSON response data to be used for highlighting missing fields on the 
            # investigation page (orange highlighting currently)
            response_data['field_labels'] = updated_incident.get_field_ids()
            response_data['missing_fields'] = updated_incident.get_missing_field_verbose_names()
            response_data['missing_field_labels'] = updated_incident.get_missing_field_ids()
            
            # If the investigation is complete, instead of displaying a list of missing
            # fields, should display the date of completion.
            response_data['inv_complete'] = form.instance.investigation_complete
            if (response_data['inv_complete']):
                response_data['inv_complete_date'] = form.instance.investigation_completed_date.strftime('%B %-d, %Y, %I:%M %p')
                response_data['inv_narrative'] = form.instance.investigation_narrative
                response_data['inv_narrative_by'] = form.instance.narrative_by.get_name()
                response_data['investigator'] = form.instance.investigator.get_name()

            # Indicate to JSON if the investigation has just been completed or was
            # complete, but now is not.
            response_data['just_completed'] = False
            response_data['just_incompleted'] = False

            # Indicate to JSON if the incident is marked as valid for trending
            response_data['valid'] = form.instance.valid
            response_data['invalid_reason'] = form.instance.invalid_reason
            response_data['valid_status_by'] = form.instance.valid_status_by.get_name()
            response_data['valid_status_date'] = form.instance.investigation_completed_date

            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

            #return HttpResponseRedirect(self.get_next_url())
        else:
            return self.render_to_json_response({'errors':form.errors})
            #return HttpResponseRedirect(self.get_next_url())

    def handle_investigation_form(self, context):
        """Process updates (POSTs) to the investigation form, including the initial POST
        upon page load.

        Handles the posting of data to the investigatio form. If the form is valid, take
        the user inputted values to inform additional field changes (dates, etc). Also
        handles logic for sending email notifications based on completion status. Also
        determines which fields are missing for NSIR-RT sharing, and provides that to
        the jQuery responsible for loading the page.

        Returns:
            An HttpResponse object representing the next page to be loaded. Currently
            returning an ajax relaod of the same page, but highlighting changes made
            to the investigation.
        """
        form = context['investigation_form']
        # response_data is a dictionary, to be turned into json data, which is provided to
        # the jquery handling ajax form posts for this investigation.
        response_data = {}

        django_messages = []
        temp_just_completed = False
        temp_just_incompleted = False

        if form.is_valid():
            # Throw error if anonymous user somehow made it to investigation page:
            if self.request.user.is_anonymous():
                django_messages.append(messages.error(self.request, "Error updating Incident. You don't have the required permissions."))
                response_data['messages'] = django_messages
                return HttpResponse(json.dumps(response_data), content_type="application/json")

            # Store previous instance of incident object before most recent form POSTs are
            # saved to the DB.
            myid = self.object.incident_id
            old_incident = models.Incident.objects.get(incident_id=myid)
            prev_investigator = old_incident.investigator
            updated_incident = form.save(commit=False)
            # If the user does not have editing privileges, do not save EXCEPT if changing
            # authorized fields
            if not self.request.user.can_edit(investigator_pk=updated_incident.investigator.pk) and "investigator" not in form.changed_data:
                if (len(form.changed_data) == 0):
                    response_data["empty_post"] = True
                    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
                # If only the flagged field changed, allow the change to be saved
                if not (len(form.changed_data) == 1 and form.changed_data[0] == 'flag'):
                    response_data["blocked_post"] = True
                    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

            form.save_m2m() # Saves m2m field updates

            # Assign acute_medical_harm on the fly if local_severity_level has changed
            local_severity_changed = "local_severity_level" in form.changed_data
            if local_severity_changed:
                new_acute_pk = self.map_acute_from_local(updated_incident.local_severity_level)
                if new_acute_pk is None:
                    updated_incident.acute_medical_harm = None
                else:
                    updated_incident.acute_medical_harm = models.AcuteMedicalHarm.objects.get(pk=new_acute_pk)

            # Update investigation fields if the investigator has changed
            cur_investigator = updated_incident.investigator
            investigator_changed = "investigator" in form.changed_data
            if investigator_changed:
                updated_incident.investigation_assigned_by = self.request.user
                updated_incident.investigation_assigned_date = timezone.now()
                updated_incident.date_last_reminder = updated_incident.investigation_assigned_date
                form.changed_data.append('investigator_assigned_date')
            elif 'investigator_assigned_date' in form.changed_data:
                form.changed_data.remove('investigation_assigned_date')

            # Determine if there are missing fields in the investigation which are
            # required for NSIR-RT sharing
            required_complete = updated_incident.is_complete()
            updated_incident.investigation_complete = required_complete

            # If the investigation was just completed upon most recent POST, update the
            # datetime in the DB
            just_completed = updated_incident.investigation_complete  and len(form.changed_data) > 0
            if just_completed and updated_incident.investigation_completed_date == None:
                updated_incident.investigation_completed_date = timezone.now()
                temp_just_completed = True

            # Remove completed date if a previously-completed incident was updated so that
            # it is no longer complete.
            if not required_complete:
                if updated_incident.investigation_completed_date:
                    temp_just_incompleted = True
                updated_incident.investigation_completed_date = None

            # Assign the author of the investigation narrative if it changed
            old_narrative = old_incident.investigation_narrative
            updated_narrative = updated_incident.investigation_narrative
            if old_narrative != updated_narrative:
                if updated_narrative == "":
                    updated_incident.narrative_by = None
                else:
                    updated_incident.narrative_by = self.request.user

            # Save these changes to DB before generating email notifications
            updated_incident.save()
            if investigator_changed:
                signals.investigator_assigned.send(sender=self, incident=updated_incident)
                signals.investigator_unassigned.send(sender=self, incident=updated_incident, old_investigator=prev_investigator)

            # Only send completed investigation email to subscribers if the investigation
            # was not complete prior to the most recent POST
            just_completed_signal = updated_incident.investigation_complete and not old_incident.investigation_complete
            if just_completed_signal:
                signals.incident_completed.send(sender=self, incident=updated_incident)

            if temp_just_completed:
                messages.success(self.request, "Investigation completed!")
            elif temp_just_incompleted:
                messages.success(self.request, "Investigation successfully updated: no longer complete.")
            else:
                messages.success(self.request, "Investigation successfully updated.")

            # If the next URL to be accessed is this page (Currently always the case), 
            # prepare json data for highlighting changed fields and displaying messages
            # to the user. Otherwise redirect according to get_next_url()
            if int(self.get_next_url().split('incident')[1].replace("/", "")) == updated_incident.incident_id:
                for message in messages.get_messages(self.request):
                    django_messages.append({
                        "level": message.level,
                        "message": message.message,
                        "extra_tags": message.tags,
                    })
                response_data['messages'] = django_messages
                response_data['changed'] = form.changed_data

                # JSON response data to be used for highlighting missing fields on the 
                # investigation page (orange highlighting currently)
                response_data['field_labels'] = updated_incident.get_field_ids()
                response_data['missing_fields'] = updated_incident.get_missing_field_verbose_names()
                response_data['missing_field_labels'] = updated_incident.get_missing_field_ids()
                
                # If the investigation is complete, instead of displaying a list of missing
                # fields, should display the date of completion.
                response_data['inv_complete'] = form.instance.investigation_complete
                if (response_data['inv_complete']):
                    response_data['inv_complete_date'] = form.instance.investigation_completed_date.strftime('%B %-d, %Y, %I:%M %p')
                    response_data['inv_narrative'] = form.instance.investigation_narrative
                    response_data['inv_narrative_by'] = form.instance.narrative_by.get_name()
                    response_data['investigator'] = form.instance.investigator.get_name()

                # Indicate to JSON if the investigation has just been completed or was
                # complete, but now is not.
                response_data['just_completed'] = temp_just_completed
                response_data['just_incompleted'] = temp_just_incompleted

                # Indicate to JSON if the incident is marked as valid for trending
                response_data['valid'] = form.instance.valid
                response_data['invalid_reason'] = form.instance.invalid_reason
                if form.instance.valid_status_by != None and form.instance.valid_status_by != "":
                    response_data['valid_status_by'] = form.instance.valid_status_by.get_name()
                else:
                    response_data['valid_status_by'] = ""

                response_data['can_edit'] = self.request.user.can_edit(investigator_pk=cur_investigator.pk)

                return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
            else:
                return HttpResponseRedirect(self.get_next_url())

        # If the form POST was not valid:
        error_msg_inv = ""
        if not form.is_valid():
            error_msg_inv = " Investigation."
        messages.error(self.request, "Error updating:%s Please check form and try again." % (error_msg_inv))
        for message in messages.get_messages(self.request):
            django_messages.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
            })
        response_data['messages'] = django_messages
        response_data['errors'] = form.errors
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

    def map_acute_from_local(self, local_severity):
        """Map a level of local severity determined on an investigation chage to an NSIR choice
        for acute medical harm.

        Returns:
            An integer value representing the pk of the AcuteMedicalHarm object that should be
            assigned to the acute_medical_harm field according to input into the local_severity_level
            field.
        """
        if local_severity is None:
            return None
        elif local_severity.pk == 3: #C
            return 1 #None
        elif local_severity.pk == 4 or local_severity.pk == 5: #D or E
            return 2 #Mild
        elif local_severity.pk == 6 or local_severity.pk == 7: #F or G
            return 3 #Moderate
        elif local_severity.pk == 8: # H
            return 4 #Severe
        elif local_severity.pk == 9: #I
            return 5 #Death
        else:
            return None

    def get_object(self):
        """Get the incident instance tied to the current investigation.
        """
        return models.Incident.objects.get(incident_id=self.kwargs.get("incident_id"))


def get_field_values_view(request):
    """View function called to provide the appropriate investigation form-field value pairs
    based on the event type of the current investigation and the selected template type.
    """
    response_data = {}
    selected_type = request.POST["selected_type"]
    event_type = request.POST["event_type"]
    # RC_type = models.EventType.objects.get(slug="reportable-circumstance")
    # skip_fields_RC = ['acute_medical_harm', 'dosimetric_impact', 'latent_medical_harm']

    # Try to get type instance, if not return an error to be displayed to the user.
    try:
        type_object = models.PredefinedIncident.objects.get(name=selected_type)
    except (AttributeError, TypeError, models.PredefinedIncident.DoesNotExist):
        response_data['empty'] = True
        if selected_type != "---------":
            response_data['error_message'] = "There was a problem while trying to populate the appropriate fields for this type of incident. Please notify the system administrator."
        return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

    # Store field-value pairs to be JSONified
    fieldarray = []
    field_objects = models.PredefinedField.objects.filter(incident_type=type_object)
    for field_object in field_objects:
        field = "#id_" + field_object.model_field.field_name
        value = field_object.field_value
        fieldarray.append({"field":field,"field_value":value})
        # if not (event_type == RC_type and field_object.model_field in skip_fields_RC):
            # field = "#id_" + field_object.model_field
            # value = field_object.field_value
            # fieldarray.append({"field":field,"field_value":value})
    response_data["fields"] = fieldarray

    # Pass array of names of fields that are affected by template changes
    temp_fields = list(models.AllowedTemplateField.objects.filter(event_type__name=event_type).values_list('field_name', flat=True))
    response_data["template_fields"] = []
    for temp in temp_fields:
        response_data["template_fields"].append("#id_" + temp)

    # Need to pass required fields in case need to reapply "missing" highlighting
    required_fields = models.Incident.get_required_fields(event_type=event_type)
    response_data["required_fields"] = []
    for req in required_fields:
        response_data["required_fields"].append("#id_" + req)

    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")


def save_new_image_view(request):
    """View function called to attempt to save a new incident image
    """
    response_data = {}
    form = forms.IncidentImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        new_image = form.instance
        new_image.uploaded_by = request.user
        new_image.uploaded_date = timezone.now()
        new_image.save()
        response_data["success"] = True
        response_data["image_name"] = new_image.image_name
        response_data["image_date"] = new_image.uploaded_date.strftime('%B %-d, %Y, %-I:%M %p')
        response_data["image_uploaded_by"] = new_image.uploaded_by.get_name()
        response_data["image_location"] = new_image.image.url
    else:
        response_data["success"] = False
        response_data["errors"] = form.errors
    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

def save_new_template_view(request):
    """View function called to attempt to save a new template type based on a provided 
    list of field-value pairs. 
    """

    response_data = {}

    # Create a new TemplateForm using the POST data. The field-value pairs which should
    # be saved are included in this POST, but seem to be ignored in creating the form
    # which is good.
    form = forms.TemplateForm(request.POST) 

    if form.is_valid():
        # Create/Save the new template type
        new_type = form.instance
        new_type.created_by = request.user
        new_type.code_name = ''.join(new_type.name.split()).lower()
        new_type.save()

        # Create the associated predefined field-value pairs to be associated with the new
        # template type
        create_predefined_fields(json.loads(request.POST["fields"]), new_type)

        response_data["template_name"] = new_type.name
        response_data["template_pk"] = new_type.id
    else:
        response_data["errors"] = form.errors
    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

def create_predefined_fields(field_value_pairs, predefined_type):
    """Function used to create new instances of PredefinedField model for a provided
    PredefinedIncident model instance, based on provided field-value data.

    field_value_pairs is an array of dictionaries, with each dictionary containing entries
    for the field name and the PK of the value to fill that field.
    """
    for pair in field_value_pairs:
        fieldname = pair['field_name'][4:] # Remove '#id_' prefix
        allowed_field = models.AllowedTemplateField.objects.get(field_name=fieldname)
        try:
            fieldval = pair['field_val']
        # Needed for case where the templatable field has been removed from the investigation
        # form (e.g. when acute medical harm was removed and replaced with QC)
        except KeyError:
            fieldval = None
        if not(fieldval is None or fieldval == ""):
            # Handle multiselect fieldvals (these are passed as an array of PKs)
            # Create a PredefinedField instance for each
            if isinstance(fieldval,list):
                for val in fieldval:
                    myinstance = models.PredefinedField(model_field=allowed_field, field_value=val, incident_type=predefined_type)
                    myinstance.save()
            # Standard single value fields
            else:
                myinstance = models.PredefinedField(model_field=allowed_field, field_value=fieldval, incident_type=predefined_type)
                myinstance.save()

class News(NewPasswordMixin,TemplateView):
    """View used to display news items.
    """
    template_name = "incidents_shared/news.html"

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
            Of note here, are the added chart context variables.
        """
        context = super(News, self).get_context_data(*args, **kwargs)

        return context

class Search(NewPasswordMixin,TemplateView):
    """View used to handle searching for incidents by ID Number.
    """
    template_name = "incidents_shared/search.html"

    ERROR_ID_MESSAGE = "There is no reported incident that matches the ID you have entered."
    ERROR_KEY_MESSAGE = "There is no reported incident containing the provided text."
    BLANK_MESSAGE = "No search parameter provided. Please enter an incident ID or keyword."
    NO_FILTER_MESSAGE = "No filters indicated. Please include one or more search filters."

    def is_number(self, str):
        """Test if a string is an integer.

        Used to determine if the provided search string is just and incident ID.
        """
        try:
            int(str)
            return True
        except ValueError:
            pass
     
        return False

    def render_to_json_response(self,context,**response_kwargs):
        """Function which renders the report page when the request is an ajax request.

        Render the report page (template) via an ajax request. Such a request is made when
        searching for an incident.

        Args:
            response_kwargs: dictionary containing keys 'anonymous_user', 'incident_id',
            'summary_url', and 'investigation_url'. These are a boolean indicating if
            the user is logged in, the unique incident ID, and summaries URLs of the
            corresponding summary and investigation pages respectively.

        Returns:
            Returns an HttpResponse object to load the current page, and display links to
            the user, which differ based on whether or not the user is logged in.
        """
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def post(self, request, *args, **kwargs):
        """Handle processing of the POST'd search request and filters.

        Parse the POST parameters relevant to the incident search, query for incidents
        in the DB accordingly, and return the formatted results.

        Returns:
            Returns and HttpResponse object to load the current page, with JSONified data
            including keys for:
            anonymous_user - Boolean indicating if user who made the request is logged in or no
            incident_array - array of dictionaries, each of which represents an incident and the
                data to be displayed in a table to the user
            query_string - the query string that was submitted by the user (returned to allow
                highlighting)
        """
        query_string = self.request.POST.get('search_query')
        filter_inc_id = self.request.POST.get('filter_inc_id')
        filter_pt_id = self.request.POST.get('filter_pt_id')
        filter_text = self.request.POST.get('filter_text')

        # If the query is empty:
        if query_string.strip() == '':
            return self.render_to_json_response({'blank_message':self.BLANK_MESSAGE})
        # If no filters are included:
        elif filter_inc_id == None and filter_pt_id == None and filter_text == None:
            return self.render_to_json_response({'blank_message':self.NO_FILTER_MESSAGE})
        # Query is good, extract information accordingly
        else:
            incident_array = []  # array to hold dictionaries representing incidents
            Q_array = [] # array of Q objects (to be OR'd) when making the single query
            # If filtering by Incident ID
            if filter_inc_id:
                try:
                    query_id = int(query_string)
                    Q_array.append(Q(incident_id=query_id))
                except ValueError:
                    pass
            # If filtering by Patient ID
            if filter_pt_id:
                Q_array.append(Q(patient_id=query_string))
            # If filtering by description text
            if filter_text:
                Q_array.append(Q(incident_description__icontains=query_string))

            # Make the incident query if the Q_array isn't empty
            # This is needed if Incident ID is only search parameter, and there are no matches
            if len(Q_array) > 0:
                query_incidents = models.Incident.objects.filter(reduce(operator.or_, Q_array))
            else:
                query_incidents = []

            # Format the matching incidents into dictionaries
            for inc in query_incidents:
                inc_dict = {
                    "incident_id": inc.incident_id,
                    "summary_url": reverse('incidents_nsir:incident-summary', kwargs={'incident_id': inc.incident_id}),
                    # "descriptor": inc.descriptor,
                    "description": inc.incident_description,
                    "date_incident_detected": inc.date_incident_detected.strftime('%B %-d, %Y'),
                }
                # Only include patient ID matches and links to the investigation if the user is logged in
                if(not self.request.user.is_anonymous()):
                    inc_dict["investigation_url"] = reverse('incidents_nsir:incident', kwargs={'incident_id': inc.incident_id})
                    inc_dict["patient_id"] = inc.patient_id
                incident_array.append(inc_dict)

            return self.render_to_json_response({'anonymous_user':self.request.user.is_anonymous(),'incident_array':incident_array, 'query_string':query_string})

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
            Of note here, are the added chart context variables.
        """
        context = super(Search, self).get_context_data(*args, **kwargs)

        query_model = get_model('incidents_nsir','EventType')
        context["chart_0_context"] = self.prepare_chart_context(query_model=query_model)
        query_model = get_model('incidents_nsir','Diagnosis')
        context["chart_1_context"] = self.prepare_chart_context(query_model=query_model)
        query_model = get_model('incidents_nsir','FunctionalWorkArea')
        context["chart_2_context"] = self.prepare_chart_context(query_model=query_model)

        # context["chart_context"] = chart_context
        return context

    def prepare_chart_context(self,query_model):
        """Prepare a context dictionary, which is JSONified, to be used in generating a 
        stacked column (date-binned) highchart for an FK model.
        """
        chart_context = {}
        parameter_type = models.StatParameterType.objects.get(type_name="key_field")
        plot_type = "column"
        chart_context["plot_type"] = plot_type
        chart_context["query_model_title"] = query_model._meta.verbose_name.title()
        chart_context["query_model_title_plural"] = query_model._meta.verbose_name_plural.title()
        query_field = None
        for field in models.Incident._meta.fields:
            if field.get_internal_type() == "ForeignKey":
                if field.rel.to == query_model:
                    query_field = field
                    break
        fk_choice = "All"
        chart_context["single_choice"] = None
        query_complete = "all"
        complete_object = models.StatCompletionFilter.objects.get(filter_name=query_complete)
        complete_label = complete_object.name
        chart_context["complete_label"] = complete_label
        query_dates = "date_incident_detected"
        date_object = models.StatDateType.objects.get(field_name=query_dates)
        date_label = models.Incident._meta.get_field_by_name(query_dates)[0].verbose_name
        chart_context["date_label"] = date_label
        bin_object = models.StatDateBin.objects.get(bin_name="monthly_last_year")
        date_dict = statistics.handle_dates(form=None,response_data=chart_context,bin_object=bin_object)
        series_array = statistics.get_counts_key(bin_object=bin_object,query_range=date_dict['query_range'],query_model=query_model,fk_choice=fk_choice,query_field=query_field,query_dates=query_dates,query_complete=query_complete,start_date=date_dict["start_date"],end_date=date_dict["end_date"])
        chart_context["series_array"] = series_array
        chart_context = json.dumps(chart_context,cls=DjangoJSONEncoder)

        return chart_context


class IncidentSummary(NewPasswordMixin, DetailView):
    """View used to display summary information for a particular incident/investigation.
    """
    template_name = "incidents_nsir/incident_summary_nsir.html"
    model = models.Incident

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
        """
        context = super(IncidentSummary, self).get_context_data(*args, **kwargs)
        incident = self.object

        context["incident"] = incident
        context["investigator"] = incident.investigator
        context["comp"] = incident.investigation_complete
        context["ameliorating_acts"] = incident.ameliorating_actions.all()
        context["risk_acts"] = incident.actions_reduce_risk.all()
        context["acts_comp"] = False
        context["flag"] = incident.flag
        context["discussed"] = incident.discussion
        context["shared"] = False

        # OLD VERSION OF FLOWCHART (WHEN USING PAPER FORMS)
        # if incident.submitted:
        #     context["submitted_class"] = "color_complete"
        # else:
        #     context["submitted_class"] = "color_incomplete"

        # if incident.investigator:
        #     context["investigator_class"] = "color_complete"
        # else:
        #     context["investigator_class"] = "color_incomplete"

        # if incident.investigation_complete or not incident.valid:
        #     context["investigation_class"] = "color_complete"
        # elif not incident.investigator:
        #     context["investigation_class"] = "color_incomplete"
        # else:
        #     context["investigation_class"] = "color_progress"

        # if incident.discussion:
        #     context["discussion_class"] = "color_complete"
        # elif incident.flag:
        #     context["discussion_class"] = "color_progress"
        # else:
        #     context["discussion_class"] = "color_incomplete"

        # Assign classes to flowchart items for coloring:
        context["incident_class"] = "color_incident"

        if incident.submitted:
            context["report_class"] = "color_complete"
        else:
            context["report_class"] = "color_incomplete"

        if incident.submitted_by:
            if incident.submitted_by.role.pk == 4:
                context["coordinator_class"] = "color_complete"
            else:
                context["coordinator_class"] = "color_incomplete"

        if incident.investigator:
            context["investigator_class"] = "color_complete"
        else:
            context["investigator_class"] = "color_incomplete"

        if incident.submitted:
            context["submit_class"] = "color_complete"
        else:
            context["submit_class"] = "color_incomplete"

        if incident.investigation_complete or not incident.valid:
            context["investigation_class"] = "color_complete"
        elif not incident.investigator:
            context["investigation_class"] = "color_incomplete"
        else:
            context["investigation_class"] = "color_progress"

        if incident.discussion:
            context["discussion_class"] = "color_complete"
        elif incident.flag:
            context["discussion_class"] = "color_progress"
        else:
            context["discussion_class"] = "color_incomplete"

        # Get actions for the incident, and assign colors to the actions piece
        # Add coloration for flowchart items to indicated

        actionsList = models.IncidentAction.objects.filter(incident=incident)
        actionsCount = actionsList.count()

        actionsCompleteList = models.IncidentAction.objects.filter(
            Q(incident=incident),
            Q(complete=True),
        )
        actionsCompleteCount = actionsCompleteList.count()

        actionsIncompleteList = models.IncidentAction.objects.filter(
            Q(incident=incident),
            Q(complete=False),
        )
        actionsIncompleteCount = actionsIncompleteList.count()
        
        if actionsCount == 0:
            context["action_class"] = "color_incomplete"
        elif actionsIncompleteCount == 0:
            context["action_class"] = "color_complete"
        else:
            context["action_class"] = "color_progress"

        context["actions_count"] = actionsCount
        context["actions_list"] = actionsList
        context["actions_complete_count"] = actionsCompleteCount
        context["actions_complete_list"] = actionsCompleteList
        context["actions_incomplete_count"] = actionsIncompleteCount
        context["actions_incomplete_list"] = actionsIncompleteList

        return context

    def get_object(self):
        return models.Incident.objects.get(incident_id=self.kwargs.get("incident_id"))


class Statistics(NewPasswordMixin, FormView):
    """View used to display the Statistics page of SaILS.

    This view is used to handle input to a statistics form which allows users to specify
    the nature of an incident plot they wish to generate. Also handle passing necessary
    JSON data to jQuery to create these charts dynamically.
    """
    template_name = "incidents_nsir/statistics_nsir.html"
    form_class = forms.StatisticsForm
    success_url = "/nsir/statistics/"

    # REMOVE THIS
    def get_initial(self):
        """Determine which form values should be initialized.

        Temporarily setting initial values for speed of producing test plots.

        Returns:
            A dictionary whose keys are form fields and whose values are the initial
            values to be filled in.
        """
        initial = super(Statistics, self).get_initial()
        # initial['plot_type'] = models.StatPlotType.objects.get(name="Pie Chart")
        initial['parameter_type'] = models.StatParameterType.objects.get(name="NSIR-RT Field")
        initial['completion_filter'] = models.StatCompletionFilter.objects.get(name="All Valid Incidents")
        initial['date_type'] = models.StatDateType.objects.get(name="Date Incident Detected")
        # initial['fk_model_type'] = models.StatFKModelChoice.objects.get(name="Event Type")
        initial['date_bin'] = models.StatDateBin.objects.get(name="Monthly - Last Year")
        initial['fk_single_choice'] = "All"
        # initial['start_month'] = models.Month.objects.get(name="April")
        # initial['end_month'] = models.Month.objects.get(name="March")
        # initial['start_year'] = 2015
        # initial['end_year'] = 2016
        return initial

    def get_error_message(self,field_label):
        """Produce an error message that describes an error in the form data.
        """
        return "There is a problem with the choice you selected for '%s'. Please notify the system administrator" % (field_label)

    def form_valid(self, form):
        """When valid form data has been POSTed.

        Extract the pertinent form field values, and use these to formulate the needed
        JSON objects to pass to jQuery and produce plots corresponding to the field values.
        When successful (i.e. the form data makes sense), store these parameters in
        response_data dictionary to be JSONified. Call appropriate handler functions based
        on the type of parameter being plotted, to fill the response_data dictionary.

        Args:
            form: Accept the current (filled) form.

        Returns:
            An HttpResponse object that redirects user to the same page. If the request is
            ajax, return current filled in form. If the request is not ajax, return a
            fresh (empty) report page. Current implementation uses ajax requests.
        """
        # Call the parent version, which includes saving the instance
        response = super(Statistics, self).form_valid(form)

        response_data = {}

        parameter_type = form.cleaned_data['parameter_type']
        if parameter_type.type_name == "key_field":
            self.handle_key_plot(form=form,response_data=response_data)
        elif parameter_type.type_name == "user_field":
            self.handle_user_plot(form=form,response_data=response_data)

        if self.request.is_ajax():
            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            return response

    def handle_user_plot(self,form,response_data):
        """Prepare response_data dictionary required for plots of ILSUsers.

        Retrieve cleaned, valid form inputs to create required key-value pairs in the
        response_data dictionary.

        Args:
            form: Accep the cleaned, valid (filled) form.
            response_data: dictionary of data which is to be JSONified to generated plots
        """
        # Getting chart type
        current_field = 'plot_type'
        plot_type = form.cleaned_data[current_field]
        response_data['plot_type'] = plot_type.type_name

        current_field = 'user_type'
        # user_type holds Statistics object, e.g. Investigator or Oncologist 
        user_type = form.cleaned_data[current_field]
        user_model = ILSUser
        response_data["query_model_title"] = user_type.name
        response_data["query_model_title_plural"] = user_type.name 

        current_field = 'user_single_choice'
        user_choice = form.cleaned_data[current_field]
        if user_choice == "All":
            response_data["single_choice"] = None
        else:
            response_data["single_choice"] = user_model.objects.get(id=user_choice).get_name()

        # Completion status
        current_field = 'completion_filter'
        complete_object = form.cleaned_data[current_field]
        # Simple lowercase name of completeness filter, for logic of filtering Incident objects
        # e.g. query_complete = complete
        query_complete = complete_object.filter_name
        # Readable name of the completeness filter, for displaying on the plot
        # e.g. query_label = Completed Incidents
        complete_label = complete_object.name
        response_data["complete_label"] = complete_label

        # Date label
        # Handle the date type to plot on x-axis
        # e.g. query_dates = date_incident_detected
        current_field = 'date_type'
        date_object = form.cleaned_data[current_field]
        query_dates = date_object.field_name
        # Throw error if no date field in Incident model matches the Statistics Model choice
        try:
            date_label = models.Incident._meta.get_field_by_name(query_dates)[0].verbose_name    
        except FieldDoesNotExist:
            response_data["error_message"] = self.get_error_message(form.fields[current_field].label)
            return
        response_data["date_label"] = date_label

        date_dict = statistics.handle_dates(form=form, response_data=response_data)
        if date_dict == None:
            return

        # {array of dicts} e.g. [{'data':[6,19,4,...], 'name':EventType}, {...}]
        # Each element in the array value of 'data' key is # counts in a bin
        series_array = statistics.get_counts_user(bin_object=form.cleaned_data['date_bin'], query_range=date_dict['query_range'], query_model=user_model, user_type=user_type, user_choice=user_choice, query_dates=query_dates, query_complete=query_complete, start_date=date_dict['start_date'], end_date=date_dict['end_date'])
        
        # get the number of incidents that forms the denominator of each chart piece's
        # fractional value
        num_incidents = statistics.get_num_incidents(query_dates=query_dates,start_date=date_dict['start_date'],end_date=date_dict['end_date'],query_complete=query_complete,query_field=user_type.incident_field_name)
        response_data["num_incidents"] = num_incidents

        # Always reformat for unstacked column (just reassigns the 'points' data to the
        # 'data' key... Need to do this because of how was set up originally)
        if response_data["plot_type"] == "column":
            series_array = statistics.format_series_for_stacked(series_array=series_array, num_incidents=num_incidents)

        # Reformat data as needed if plotting a pie or unstacked column chart
        if response_data["plot_type"] == "pie":
            series_array = statistics.format_series_for_pie(series_array=series_array,date_range=response_data['date_range'],query_model_title=response_data["query_model_title"], num_incidents=num_incidents)
        elif response_data["plot_type"] == "unstacked":
            x_bins = []
            series_array = statistics.format_series_for_unstacked(series_array=series_array, x_bins=x_bins, num_incidents=num_incidents)
            response_data["date_range"] = x_bins

        response_data["series_array"] = series_array

        return   


    def handle_key_plot(self,form,response_data):
        """Prepare response_data dictionary required for plots of any model related to
        the Incident model via a key based relationship.

        Retrieve cleaned, valid form inputs to create required key-value pairs in the
        response_data dictionary. This method handles models related to the Incident model
        via ForeignKey, ManyToMany, TreeForeignKey, or TreeManyToMany.

        Args:
            form: Accep the cleaned, valid (filled) form.
            response_data: dictionary of data which is to be JSONified to generated plots
        """
        # Getting chart type
        current_field = 'plot_type'
        plot_type = form.cleaned_data[current_field]
        response_data['plot_type'] = plot_type.type_name

        # Model to be Plotted
        # e.g. query_model = <class 'incidents_nsir.models.EventType'>
        current_field = 'fk_model_type'
        model_object = form.cleaned_data[current_field]
        query_model = get_model('incidents_nsir',model_object.model_name)
        # Throw error if no matching model to the Statistics Model choice
        if query_model == None:
            response_data["error_message"] = self.get_error_message(form.fields[current_field].label)
            return

        response_data["query_model_title"] = query_model._meta.verbose_name.title()
        response_data["query_model_title_plural"] = query_model._meta.verbose_name_plural.title() 

        # Get the Incident modelfield associated via FK with the query_model
        # e.g. if query_model = <class 'incidents_nsir.models.EventType'>, query_field = <django.db.models.fields.related.ForeignKey: event_type>
        # Attributes: query_field.name and query_field.get_internal_type()
        query_field = None
        for field in models.Incident._meta.many_to_many:
            if field.rel.to == query_model:
                query_field = field
        if query_field == None:
            for field in models.Incident._meta.fields:
                if field.get_internal_type() == "ForeignKey" or field.get_internal_type() == "TreeForeignKey":
                    if field.rel.to == query_model:
                        query_field = field
           
        # Choice filter
        current_field = 'fk_single_choice'
        fk_choice = form.cleaned_data[current_field]
        # fk_choice = "All"

        if fk_choice == "All":
            response_data["single_choice"] = None
        else:
            response_data["single_choice"] = fk_choice

        # Completion status
        current_field = 'completion_filter'
        complete_object = form.cleaned_data[current_field]
        # Simple lowercase name of completeness filter, for logic of filtering Incident objects
        # e.g. query_complete = complete
        query_complete = complete_object.filter_name
        # Readable name of the completeness filter, for displaying on the plot
        # e.g. query_label = Completed Incidents
        complete_label = complete_object.name
        response_data["complete_label"] = complete_label

        # Date label
        # Handle the date type to plot on x-axis
        # e.g. query_dates = date_incident_detected
        current_field = 'date_type'
        date_object = form.cleaned_data[current_field]
        query_dates = date_object.field_name
        # Throw error if no date field in Incident model matches the Statistics Model choice
        try:
            date_label = models.Incident._meta.get_field_by_name(query_dates)[0].verbose_name    
        except FieldDoesNotExist:
            response_data["error_message"] = self.get_error_message(form.fields[current_field].label)
            return
        response_data["date_label"] = date_label

        date_dict = statistics.handle_dates(form=form, response_data=response_data)
        if date_dict == None:
            return

        # {array of dicts} e.g. [{'data':[6,19,4,...], 'name':EventType}, {...}]
        # Each element in the array value of 'data' key is # counts in a bin
        series_array = statistics.get_counts_key(bin_object=form.cleaned_data['date_bin'], query_range=date_dict['query_range'], query_model=query_model, fk_choice=fk_choice, query_field=query_field, query_dates=query_dates, query_complete=query_complete, start_date=date_dict['start_date'], end_date=date_dict['end_date'])
        
        # get the number of incidents that forms the denominator of each chart piece's
        # fractional value
        num_incidents = statistics.get_num_incidents(query_dates=query_dates,start_date=date_dict['start_date'],end_date=date_dict['end_date'],query_complete=query_complete,query_field=query_field.name)
        response_data["num_incidents"] = num_incidents

        # Always reformat for unstacked column (just reassigns the 'points' data to the
        # 'data' key... Need to do this because of how was set up originally)
        if response_data["plot_type"] == "column":
            series_array = statistics.format_series_for_stacked(series_array=series_array, num_incidents=num_incidents)

        # Reformat data as needed if plotting a pie or unstacked column chart
        if response_data["plot_type"] == "pie":
            series_array = statistics.format_series_for_pie(series_array=series_array,date_range=response_data['date_range'],query_model_title=response_data["query_model_title"], num_incidents=num_incidents)
        elif response_data["plot_type"] == "unstacked":
            x_bins = []
            series_array = statistics.format_series_for_unstacked(series_array=series_array, x_bins=x_bins, num_incidents=num_incidents)
            response_data["date_range"] = x_bins
        response_data["series_array"] = series_array

        return

    def form_invalid(self, form):
        """When invalid form data has been POSTed.

        Overriding the parent method to allow for processing request as ajax.

        Args:
            form: Accept the current (filled) form.

        Returns:
            An HttpResponse object that redirects user to the same page. If the request is
            ajax, return current filled in form. If the request is not ajax, return a
            fresh (empty) report page. Current implementation uses ajax requests.
        """
        response = super(Statistics,self).form_invalid(form)

        response_data = {}

        response_data["errors"] = form.errors

        if self.request.is_ajax():
            return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")
        else:
            return response

    def get_context_data(self, *args, **kwargs):
        context = super(Statistics, self).get_context_data(*args, **kwargs)

        return context

def reload_user_choices_view(request):
    """View function called to reload the available single choices in the Statistics page
    for User type fields.
    """
    response_data = {}

    cur_model = request.POST["cur_model"]
    
    try:
        model_object = models.StatUserChoice.objects.get(name=cur_model)
    except (AttributeError, TypeError, models.StatUserChoice.DoesNotExist):
        response_data['empty'] = True
        return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

    filter_kwargs = {
        model_object.account_field_name: True
    }
    user_q = Q(**filter_kwargs)

    query_result = ILSUser.objects.filter(user_q)

    response_data["user_ids"] = list(query_result.values_list('id', flat=True))

    name_list = []
    for user in query_result:
        name_list.append(user.get_name())
    response_data["user_names"] = name_list

    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

def reload_fk_choices_view(request):
    """View function called to reload the available single choices in the Statistics page
    for NSIR-RT ForeignKey type fields.
    """
    response_data = {}
    cur_model = request.POST["cur_model"]

    try:
        model_object = models.StatFKModelChoice.objects.get(name=cur_model)
    except (AttributeError, TypeError, models.StatFKModelChoice.DoesNotExist):
        response_data['empty'] = True
        return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")

    model_class = get_model('incidents_nsir',model_object.model_name)
    if model_class == None:
        response_data['empty'] = True
        response_data['error_message'] = "There is a problem with the choice you selected for Parameter to Plot Events By. Please notify the system administrator"
        return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")


    response_data["choices"] = list(model_class.objects.all().values_list('name', flat=True))

    return HttpResponse(json.dumps(response_data, cls=DjangoJSONEncoder), content_type="application/json")



class Dashboard(StaffRequiredMixin, LoginRequiredMixin, NewPasswordMixin, TemplateView):
    """View used to display dashboard information for the current logged in user.
    """
    template_name = "incidents_nsir/dashboard_nsir.html"

    def post(self, request, *args, **kwargs):
        """Used when updating user preferences regarding notifications.
        """
        investigations = request.POST.get("investigations") == "on"
        actions = request.POST.get("actions") == "on"
        # sharings = request.POST.get("sharings") == "on"
        self.request.user.investigation_notifications = investigations
        self.request.user.action_notifications = actions
        # self.request.user.sharing_notifications = sharings
        self.request.user.save()
        messages.success(request, "Successfully updated your preferences")

        return HttpResponseRedirect(reverse("incidents_nsir:dashboard"))

    def add_summary_items(self, context):
        """Add summary items each time page is loaded.

        This method is tied to the 'Summary' section of the Dashboard. This method adds a
        a new key-value pair to the context dictionary. The value of this pair is an array
        of summary items to be displayed.
        """
        triage = models.Incident.triage.count()

        # Consider last 4 weeks of incidents
        last_4_weeks = timezone.now() - timezone.timedelta(4 * 7)
        incs = models.Incident.objects.filter(submitted__gte=last_4_weeks)

        counts = collections.Counter()
        for inc in incs:
            counts[inc.event_type] += 1

        # holds the number of events by type (reportable circumstance, near miss, etc) for the last 4 weeks

        #type_counts = ["%d %s" % (cnt, itype) for itype, cnt in counts.items()]
        type_counts = []
        for itype,cnt in counts.items():
            if itype == models.EventType.objects.get(name="Near miss"):
                type_counts.append("%d %ses" % (cnt, itype))
            else:
                type_counts.append("%d %ss" % (cnt, itype))


        # formatted output to be displayed on Dashboard
        items = [
            # ("Triage:",
            #  'There are currently %d incidents awaiting <a href="%s">triage</a>' % (triage, reverse('incidents_nsir:triage-incidents'),)),
            ("Last 4 weeks:", ", ".join(type_counts)),
        ]
        context["summary_items"] = items

    def get_context_data(self, *args, **kwargs):
        """Supply template with context values to allow for dynamic html generation.

        Returns:
            A dictionary whose key-value pairs may be accessed within the template. I.e.
            a dictionary representing a template context.
        """
        context = super(Dashboard, self).get_context_data(*args, **kwargs)

        qs = models.Incident.objects.user_incomplete(self.request.user)
        #qs = qs.select_related("incident", "incident__severity")
        context['user_incomplete_investigations'] = qs

        incidentactions = models.IncidentAction.objects.filter(responsible=self.request.user, complete=False)
        #incidentactions = incidentactions.select_related("action_type", "incident", "assigned_by")
        #incidentsharings = models.IncidentSharing.objects.filter(responsible=self.request.user, done=False)

        context["user_actions"] = incidentactions
        #context["user_sharings"] = incidentsharings

        context["user_is_oncologist"] = self.request.user.is_oncologist
        if self.request.user.is_oncologist:
            context["oncologist_incidents"] = models.Incident.objects.filter(investigation_complete=False, oncologist=self.request.user)
        else:
            context["oncologist_incidents"] = None

        # self.add_incident_counts(context)
        self.add_summary_items(context)

        query_model = get_model('incidents_nsir','EventType')
        context["chart_0_context"] = self.prepare_chart_context(query_model=query_model)
        query_model = get_model('incidents_nsir','Diagnosis')
        context["chart_1_context"] = self.prepare_chart_context(query_model=query_model)
        query_model = get_model('incidents_nsir','FunctionalWorkArea')
        context["chart_2_context"] = self.prepare_chart_context(query_model=query_model)

        return context

    def prepare_chart_context(self,query_model):
        """Prepare a context dictionary, which is JSONified, to be used in generating a 
        stacked column (date-binned) highchart for an FK model.
        """
        chart_context = {}
        parameter_type = models.StatParameterType.objects.get(type_name="key_field")
        plot_type = "column"
        chart_context["plot_type"] = plot_type
        chart_context["query_model_title"] = query_model._meta.verbose_name.title()
        chart_context["query_model_title_plural"] = query_model._meta.verbose_name_plural.title()
        query_field = None
        for field in models.Incident._meta.fields:
            if field.get_internal_type() == "ForeignKey":
                if field.rel.to == query_model:
                    query_field = field
                    break
        fk_choice = "All"
        chart_context["single_choice"] = None
        query_complete = "all"
        complete_object = models.StatCompletionFilter.objects.get(filter_name=query_complete)
        complete_label = complete_object.name
        chart_context["complete_label"] = complete_label
        query_dates = "date_incident_detected"
        date_object = models.StatDateType.objects.get(field_name=query_dates)
        date_label = models.Incident._meta.get_field_by_name(query_dates)[0].verbose_name
        chart_context["date_label"] = date_label
        bin_object = models.StatDateBin.objects.get(bin_name="monthly_last_year")
        date_dict = statistics.handle_dates(form=None,response_data=chart_context,bin_object=bin_object)
        series_array = statistics.get_counts_key(bin_object=bin_object,query_range=date_dict['query_range'],query_model=query_model,fk_choice=fk_choice,query_field=query_field,query_dates=query_dates,query_complete=query_complete,start_date=date_dict["start_date"],end_date=date_dict["end_date"])
        chart_context["series_array"] = series_array
        chart_context = json.dumps(chart_context,cls=DjangoJSONEncoder)

        return chart_context



class BaseIncidentsList (StaffRequiredMixin,LoginRequiredMixin,NewPasswordMixin, BaseListableView):
    """Parent view used to for pages which list incidents in a jquery dataTable according
    to various filters defined in child views (defined below).

    The columns syntax supplied here is compatible with that required for the 3rd party
    listable package.
    """
    model = models.Incident

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__pk", widget=SELECT),
            C(field="oncologist", ordering="oncologist__username", filtering="oncologist__pk", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
            C(field="investigation_complete", ordering="investigation_complete", filtering=False, header="Completion Status"),
        ]
    else:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
            C(field="oncologist", ordering="oncologist__username", filtering="oncologist__username", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
            C(field="investigation_complete", ordering="investigation_complete", filtering=False, header="Completion Status"),
        ]

    def date_incident_detected(self,obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/date_detected.html')
        return tmp.render(context)

    def submitted(self,obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/date_submitted.html')
        return tmp.render(context)

    def flag(self, obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/incident_flag.html')
        return tmp.render(context)

    def get_save_and_continue(self, obj):
        return False

    # Template is used to link to the relevant incident/investigation page
    def incident_id(self, obj):
        context = Context({"incident": obj})

        tmp = get_template('incidents_shared/incident_link.html')
        return tmp.render(context)

    def investigation_complete(self,obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/investigation_complete.html')
        return tmp.render(context)


class AllIncidentsList (BaseIncidentsList):
    """Display all incidents in the DB.
    """
    template_name = "incidents_shared/all_incidents_list.html"

class TriageIncidentsList(BaseIncidentsList):
    """Display all incidents without an investigator assigned.
    """
    queryset = models.Incident.triage.all()
    template_name = "incidents_shared/triage_incidents_list.html"

    columns = [
        C(field="flag", ordering="flag", filtering=False),
        C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
        C(field="descriptor", ordering=False, filtering=True),
        C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
        C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
        C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
    ]

class CompleteIncidentsList(BaseIncidentsList):
    """Display all incidents with complete investigations.
    """
    queryset = models.Incident.complete.all()
    template_name = "incidents_shared/complete_incidents_list.html"

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__pk", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="investigation_completed_date", ordering="investigation_completed_date", filtering=False, header="Date Investigation Completed"),
            C(field="valid", ordering="valid", filtering=False, header="Valid Status"),
        ]
    else:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="investigation_completed_date", ordering="investigation_completed_date", filtering=False, header="Date Investigation Completed"),
            C(field="valid", ordering="valid", filtering=False, header="Valid Status"),
        ]

    def investigation_completed_date(self,obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/date_investigation_complete.html')
        return tmp.render(context)

    def valid(self,obj):
        context = Context({"incident": obj})
        tmp = get_template('incidents_shared/incident_valid.html')
        return tmp.render(context)

class IncompleteIncidentsList(BaseIncidentsList):
    """Display all incidents with incomplete investigations.
    """
    queryset = models.Incident.incomplete.all()
    template_name = "incidents_shared/incomplete_incidents_list.html"

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__pk", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
        ]
    else:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
        ]

class IncompleteAndFlaggedIncidentsList(BaseIncidentsList):
    """Display all flagged incidents with incomplete investigations.
    """
    queryset = models.Incident.incomplete_and_flagged.all()
    template_name = "incidents_shared/incomplete_flagged_incidents_list.html"

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="flag", ordering=False, filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__pk", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
        ]
    else:
        columns = [
            C(field="flag", ordering=False, filtering=False),
            C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
        ]

class FlaggedIncidentsList(BaseIncidentsList):
    """Display all flagged incidents.
    """
    queryset = models.Incident.flagged.all()
    template_name = "incidents_shared/flagged_incidents_list.html"

    # columns = [
    #     C(field="flag", ordering=False, filtering=False),
    #     C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
    #     C(field="descriptor", ordering=False, filtering=True),
    #     C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
    #     C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
    #     C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
    #     C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
    # ]

class ActualIncidentsList(BaseIncidentsList):
    """Display all actual incidents (not RC or NM).
    """
    queryset = models.Incident.actuals.all()
    template_name = "incidents_shared/actual_incidents_list.html"

class InvalidIncidentsList(BaseIncidentsList):
    """Display all invalid incidents
    """
    queryset = models.Incident.objects.filter(valid=False)
    template_name = "incidents_shared/invalid_incidents_list.html"

class MyIncidentsList(BaseIncidentsList):
    """Display all incidents submitted by the current user.
    """
    template_name = "incidents_shared/mysubmitted_incidents_list.html"

    def get_queryset(self):
        qs = super(MyIncidentsList, self).get_queryset()
        return qs.filter(submitted_by=self.request.user)

class MyInvestigationsList(BaseIncidentsList):
    """Display all incidents with investigations assigned to the current user.
    """
    template_name = "incidents_shared/my_investigations_list.html"

    columns = [
        C(field="flag", ordering="flag", filtering=False),
        C(field="incident_id", ordering=True, header="ID",filtering="incident_id__exact"),
        C(field="descriptor", ordering=False, filtering=True),
        C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
        C(field="investigation_assigned_date",ordering="investigation_assigned_date", filtering=False, header="Date Investigation Assigned"),
        C(field="investigation_complete",ordering="investigation_complete",filtering=False,header="Completion Status"),
        C(field="valid",ordering="valid",filtering=False,header="Valid Incident"),
        C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
    ]

    def get_queryset(self):
        qs = super(MyInvestigationsList, self).get_queryset()
        return qs.filter(investigator=self.request.user)

class MyPatientsList(BaseIncidentsList):
    """Display all incidents whose oncologist is the current user.
    """
    template_name = "incidents_shared/my_patients_list.html"

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="Incident ID",filtering="incident_id__exact"),
            C(field="patient_id", ordering=True, header="Patient ID",filtering="patient_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__id", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
            C(field="investigation_complete", ordering="investigation_complete", filtering=False, header="Completion Status"),
        ]
    else:
        columns = [
            C(field="flag", ordering="flag", filtering=False),
            C(field="incident_id", ordering=True, header="Incident ID",filtering="incident_id__exact"),
            C(field="patient_id", ordering=True, header="Patient ID",filtering="patient_id__exact"),
            C(field="descriptor", ordering=False, filtering=True),
            C(field="investigator", ordering="investigator__username", filtering="investigator__username", widget=SELECT),
            C(field="date_incident_detected", ordering="date_incident_detected", filtering=False, header="Date Incident Detected"),
            C(field="submitted",ordering="submitted", filtering=False, header="Date Incident Submitted"),
            C(field="event_type", ordering=True, filtering="event_type__name", widget=SELECT, header="Event Type"),
            C(field="investigation_complete", ordering="investigation_complete", filtering=False, header="Completion Status"),
        ]

    def get_queryset(self):
        qs = super(MyPatientsList, self).get_queryset()
        return qs.filter(oncologist=self.request.user)


class BaseActionsList (StaffRequiredMixin,LoginRequiredMixin,NewPasswordMixin, BaseListableView):
    """Parent view used to for pages which list actions in a jquery dataTable according
    to various filters defined in child views (defined below).

    The columns syntax supplied here is compatible with that required for the 3rd party
    listable package.
    """
    model = models.IncidentAction

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="incident", ordering=True, header="Incident ID",filtering="incident__incident_id__exactfi"),
            C(field="action_id", ordering=True, header="Action ID",filtering="action_id__exact"),
            C(field="responsible", ordering="responsible__username", filtering="responsible__pk", widget=SELECT),
            C(field="assigned_by", ordering="assigned_by__username", filtering="assigned_by__pk", widget=SELECT),
            C(field="date_assigned",ordering="date_assigned", filtering=False, header="Date Assigned"),
            C(field="complete", ordering="complete", filtering=False, header="Completion Status"),
            C(field="completed_by", ordering="completed_by__username", filtering="completed_by__pk", widget=SELECT),
            C(field="date_completed",ordering="date_completed", filtering=False, header="Date Completed"),
        ]
    else:
        columns = [
            C(field="incident", ordering=True, header="Incident ID",filtering="incident__incident_id__exactfi"),
            C(field="action_id", ordering=True, header="Action ID",filtering="action_id__exact"),
            C(field="responsible", ordering="responsible__username", filtering="responsible__username", widget=SELECT),
            C(field="assigned_by", ordering="assigned_by__username", filtering="assigned_by__username", widget=SELECT),
            C(field="date_assigned",ordering="date_assigned", filtering=False, header="Date Assigned"),
            C(field="complete", ordering="complete", filtering=False, header="Completion Status"),
            C(field="completed_by", ordering="completed_by__username", filtering="completed_by__username", widget=SELECT),
            C(field="date_completed",ordering="date_completed", filtering=False, header="Date Completed"),
        ]

    def incident(self,obj):
        context = Context({"incident": obj.incident})
        tmp = get_template('incidents_shared/list_field_action_incident.html')
        return tmp.render(context)

    def action_id(self,obj):
        context = Context({"action": obj})
        tmp = get_template('incidents_shared/list_field_action_action.html')
        return tmp.render(context)

    def date_assigned(self,obj):
        context = Context({"action": obj})
        tmp = get_template('incidents_shared/list_field_action_date_assigned.html')
        return tmp.render(context)

    def complete(self,obj):
        context = Context({"action": obj})
        tmp = get_template('incidents_shared/list_field_action_complete.html')
        return tmp.render(context)

    def date_completed(self,obj):
        context = Context({"action": obj})
        tmp = get_template('incidents_shared/list_field_action_date_completed.html')
        return tmp.render(context)

class AllActionsList (BaseActionsList):
    """Display all actions in the DB.
    """
    template_name = "incidents_shared/all_actions_list.html"

class IncompleteActionsList(BaseActionsList):
    """Display all incomplete actions.
    """
    template_name = "incidents_shared/incomplete_actions_list.html"

    columns = None
    if settings.ANONYMOUS_DISPLAY:
        columns = [
            C(field="incident", ordering=True, header="Incident ID",filtering="incident__incident_id__exactfi"),
            C(field="action_id", ordering=True, header="Action ID",filtering="action_id__exact"),
            C(field="responsible", ordering="responsible__username", filtering="responsible__pk", widget=SELECT),
            C(field="assigned_by", ordering="assigned_by__username", filtering="assigned_by__pk", widget=SELECT),
            C(field="date_assigned",ordering="date_assigned", filtering=False, header="Date Assigned"),
            C(field="complete", ordering="complete", filtering=False, header="Completion Status"),
        ]
    else:
        columns = [
            C(field="incident", ordering=True, header="Incident ID",filtering="incident__incident_id__exactfi"),
            C(field="action_id", ordering=True, header="Action ID",filtering="action_id__exact"),
            C(field="responsible", ordering="responsible__username", filtering="responsible__username", widget=SELECT),
            C(field="assigned_by", ordering="assigned_by__username", filtering="assigned_by__username", widget=SELECT),
            C(field="date_assigned",ordering="date_assigned", filtering=False, header="Date Assigned"),
            C(field="complete", ordering="complete", filtering=False, header="Completion Status"),
        ]

    def get_queryset(self):
        qs = super(IncompleteActionsList, self).get_queryset()
        return qs.filter(complete=False)

class CompleteActionsList(BaseActionsList):
    """Display all complete actions.
    """
    template_name = "incidents_shared/complete_actions_list.html"

    def get_queryset(self):
        qs = super(CompleteActionsList, self).get_queryset()
        return qs.filter(complete=True)

class AssignedByActionsList(BaseActionsList):
    """Display all actions assigned by the current user.
    """
    template_name = "incidents_shared/assigned_by_actions_list.html"

    def get_queryset(self):
        qs = super(AssignedByActionsList, self).get_queryset()
        return qs.filter(assigned_by=self.request.user)

class ResponsibleActionsList(BaseActionsList):
    """Display all actions for which the current user is responsible.
    """
    template_name = "incidents_shared/responsible_actions_list.html"

    def get_queryset(self):
        qs = super(ResponsibleActionsList, self).get_queryset()
        return qs.filter(responsible=self.request.user)

class MyCompleteActionsList(BaseActionsList):
    """Display all actions which the current user has completed.
    """
    template_name = "incidents_shared/my_complete_actions_list.html"

    def get_queryset(self):
        qs = super(MyCompleteActionsList, self).get_queryset()
        return qs.filter(completed_by=self.request.user)

#*******************************************************************************
# AJAX views
#*******************************************************************************
# @require_POST
# def ajax_view(request):
#     print "--------------------------"
#     print "AJAX'd!"
#     print "--------------------------"

#     patientID = request.POST.get('patientID')
#     subprocess.call(["php","incidents_nsir/php/queryTreatment.php","patientID:"+patientID])

#     print "CALLED PHP!"

#     fakedict = {}
#     fakedict['fake'] = 'fake'


#     data = json.dumps(fakedict)
#     return HttpResponse(data,content_type='application/json')