from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField

import datetime

#-----------------------------------------------------------------------------------------
# Dictionary of help texts, with key values which are the same as fields within the
# Incident model. Each help text describeds the nature of the corresponding field.
#-----------------------------------------------------------------------------------------
help = {
    #Local Info
    'predefined_type': _('Register this incident as a predefined incident type to populate common investigation fields'),
    'event_type': _('Was this event a reportable circumstance, a near miss, or an actual incident?'),
    'patient_id': _('Patient ID number (for multiple patients please separate IDs with commas)'),
    'submitted_by': _('Individual who submitted the electronic incident report'),
    'submitted': _('Date the electronic incident report was submitted'),
    'valid': _('Indicate whether or not incident is valid for tranding purposes'),
    'invalid_reason': _('Describe why the incident is not valid for trending purposes'),
    'valid_status_by': _('User who set the current valid status of the investigation'),
    'valid_status_date': _('Date the current valid status (valid or invalid) was set'),
    'duplicate': _(''),
    'duplicate_of': _(''),
    'flag': _('Flag incident for discussion at Risk Management committee meeting'),
    'discussion': _('Has the discussion for this incident been completed?'),
    'reported_by': _('First and last name of the individual who filed the initial report'),
    'reported_to': _('First and last name of the coordinator who received the initial paper report'),
    'descriptor': _('One sentence descriptor of the incident'),
    'treatment_site': _('Anatomical site of treatment delivery'),
    'oncologist': _('Primary oncologist associated with the treatment'),
    'support_required': _('Is support for staff required for this incident? If any employee who was associated with this incident feels the need for psychosocial support, they should contact their immediate supervisor. Resources are available upon request.'),
    'support_given': _('Has support been offered to staff yet?'),
    'support_description': _('Briefly describe the support required by staff'),
    'patient_support_required': _('Is support for the patient(s) required for this incident, medical or otherwise?'),
    'patient_support_given': _('Has support been offered to patient(s) yet?'),
    'patient_support_description': _('Briefly describe the support required by the patient(s)'),
    'incident_id': _('Unique incident ID'),
    'report_type': _('Is this report transcribed from a paper report, or is it being inputted directly online without a paper report?'),
    'hospital_form_id': _('The ID of the hospital-wide incident form which was filled out for this incident, if applicable'),
    'coordinator_comments': _('Additional coordinator comments (optional)'),
    #Investigation
    'investigator': _('Assign an investigator to follow-up on this incident'),
    'investigation_assigned_date': _('Date the most recent investigator was assigned to the incident'),
    'investigation_assigned_by': _('User who assigned the current investigator to the incident'),
    'investigation_complete': _('Has the investigation been completed?'),
    'investigation_completed_date': _('Date the investigation was completed'),
    'date_last_reminder': _('Date the previous investigation incomplete reminder was sent'),
    'first_reminder_sent': _('Has the first reminder to complete this investigation been sent?'),
    #Section 1 - Impact
    'incident_description': _('Briefly summarize the incident. Please avoid judgement, analysis, or accusation.'),
    'reportable_circumstance': _('A reportable circumstance is a hazard that did not involve a patient but has the potential to reach patients if not corrected'),
    'near_miss': _('A near miss is an incident that was detected before reaching the patient'),
    'acute_medical_harm': _("Degree of harm to patient (Adapted from the WHO-ICPS)"),
    'local_severity_level': _("Degree of acute harm to patient"),
    'dosimetric_impact': _("Relative to the intended doses, the tumour underdose or organ-at-risk (OAR) overdose to these structures over the course of treatment"),
    'latent_medical_harm': _("The likelihood that the incident is associated with the development of evident late morbidity or reduced probability of cure."),
    # Section 2 - Discovery
    'functional_work_area': _("The functional working areas within the radiotherapy department"),
    'date_incident_detected': _("The day, month and year that the incident was detected (YYYY-MM-DD)"),
    'date_incident_occurred': _("The day, month and year that the incident occurred (YYYY-MM-DD)"),
    'time_detected': _("Exact time the incident was detected"),
    'time_period_detected': _("Time period when the incident was detected"),
    'time_occurred': _("Exact time the incident occurred"),
    'time_period_occurred': _("Time period when the incident occurred"),
    'individual_detected': _("The health care provider(s) and or other individuals who were involved in the discovery of the incident."),
    'individual_involved': _("The health care provider(s) and or other individuals who were involved in the incident. This excludes individuals only involved in the investigation and/or follow-up of the incident."),
    # Section 3 - Patient
    'patient_month_birth': _("The month of birth of the patient involved in the incident"),
    'patient_year_birth': _("The year of birth of the patient involved in the incident"),
    'patient_gender': _("The socially constructed roles, behaviours, activities, and attributes that a given society considers appropriate for men and women."),
    'diagnosis': _("The current diagnosis of the patient, for which the patient is being treated during, at the time the incident occurred"),
    #Section 4 - Details
    'process_step_occurred': _("The point during the patient's trajectory at which the incident originated"),
    'process_step_detected': _("The point during the patient's trajectory at which the incident was discovered"),
    'problem_type': _("The problem that is most responsible for the incident."),
    'secondary_problem_type': _("Additional problem(s) that describe the occurrence of the incident"),
    'contributing_factors': _("A circumstance, action or influence which is thought to have played a part in the origin or development of an incident or to have increased the risk of an incident"),
    'number_patients_affected': _("For reportable circumstances and near misses, no patients are affected. For actual incidents indicate if one or more patients were affected."),
    'number_patients_involved': _("Indicate the number of patients involved in this incident. If more than 1, and the exact quantity is unknown, please provide a numeric estimate."),
    # Section 5 - Treatment Delivery
    'radiation_treatment_technique': _("The type(s) of treatment protocol involved in the incident"),
    'total_dose_prescribed': _("The total dose, in Gy, that was prescribed to the patient involved in the incident (NN.NN)"),
    'number_fractions_prescribed': _("The number of fractions that was included in the radiation treatment plan involved in the incident"),
    'number_fractions_incorrect': _("The number of fractions that were delivered incorrectly in the radiation treatment plan involved in the incident"),
    'hardware_manufacturer_model': _("The hardware manufacturer and model that was involved in the radiation treatment incident, if relevant"),
    'software_manufacturer_model': _("The software manufacturer and model that was involved in the radiation treatment incident, if relevant"),
    'body_region_treated': _("The treatment site(s) involved in the incident."),
    'treatment_intent': _("The purpose of the prescribed course of radiation therapy"),
    # Section 6 - Investigation
    'ameliorating_actions': _("An action taken or circumstances altered to make better or compensate any harm after an incident."),
    'safety_barriers_failed': _("A safety barrier is a physical or non-physical means planned to prevent, control, or mitigate undesired events or accidents."),
    'safety_barriers_prevented': _("A safety barrier is a physical or non-physical means planned to prevent, control, or mitigate undesired events or accidents."),
    'actions_reduce_risk': _("Prevention activities planned or implemented within the radiation treatment centre and recommendations to minimize future harm."),
    'investigation_narrative': _("Please describe the findings of the investigation and what actions have been taken to ensure this incident will not reoccur."),
    'narrative_by': _("Individual who wrote the investigation narrative."),
    'patient_disclosure': _("Was the incident disclosed to the patient?"),
}

#-----------------------------------------------------------------------------------------
# Dictionary of help texts, with key values which are the same as fields within the
# IncidentAction model. Each help text describeds the nature of the corresponding field.
#-----------------------------------------------------------------------------------------
help_act = {
    'action_id': _("ID number of a taskable action, unique per incident/investigation"),
    'description_proposed': _("Description of the proposed action to be taken"),
    'responsible': _("The user who is responsible for implementing the proposed action"),
    'assigned_by': _("The user who proposed the action"),
    'date_assigned': _("The date the action was proposed"),
    'complete': _("Indicate whether or not the action has been completed"),
    'description_performed': _("Description of the action which was taken"),
    'completed_by': _("The user who carried out implementation of the proposed action"),
    'date_completed': _("The date the action was completed"),
    'date_last_reminder': _('Date the previous reminder was sent for this action'),
    'first_reminder_sent': _('Has the first reminder for this action been sent?'),
}

#-----------------------------------------------------------------------------------------
# Dictionary of verbose labels, with key values which are the same as fields within the
# Incident model. Each verbose label provides a more readable name for the corresponding
# model field.
#-----------------------------------------------------------------------------------------
vlabel = {
    #Local Info
    'predefined_type': _('Incident Template'),
    'event_type': _('Event Type'),
    'patient_id': _('Patient ID Number'),
    'submitted_by': _('Submitted by'),
    'submitted': _('Date Incident Submitted'),
    'valid': _('Valid Incident'),
    'invalid_reason': _('Reason why Invalid'),
    'valid_status_by': _('Valid Status Set By'),
    'valid_status_date': _('Date Valid Status Set'),
    'duplicate': _('Duplicate Incident'),
    'duplicate_of': _('Duplicated Incident'),
    'flag': _('Flag for Discussion'),
    'discussion': _('Discussion Completed'),
    'reported_by': _('Reported By'),
    'reported_to': _('Reported To'),
    'descriptor': _('Incident Descriptor'),
    'treatment_site': _('Treatment Site'),
    'oncologist': _('Primary Radiation Oncologist'),
    'support_required': _('Staff Support Required?'),
    'support_given': _('Staff Support Given?'),
    'support_description': _('Staff Support Description'),
    'patient_support_required': _('Patient Support Required?'),
    'patient_support_given': _('Patient Support Given?'),
    'patient_support_description': _('Patient Support Description'),
    'incident_id': _('Incident ID'),
    'report_type': _('Type of Report'),
    'hospital_form_id': _('Hospital Incident Form ID'),
    'coordinator_comments': _('Coordinator Comments'),
    #Investigation
    'investigator': _('Investigator'),
    'investigation_assigned_date': _('Date Investigator Assigned'),
    'investigation_assigned_by': _('Investigator Assigned by'),
    'investigation_complete': _('Investigation Complete'),
    'investigation_completed_date': _('Date Invesgitation Completed'),
    'date_last_reminder': _('Date Previous Reminder Sent'),
    'first_reminder_sent': _('First Reminder Sent'),
    #Section 1 - Impact
    'incident_description': _('Incident Description'),
    'reportable_circumstance': _('Reportable Circumstance'),
    'near_miss': _('Near miss'),
    'acute_medical_harm': _("Acute Medical Harm"),
    'local_severity_level': _("Acute Incident Severity"),
    'dosimetric_impact': _("Dosimetric Impact"),
    'latent_medical_harm': _("Latent Medical Harm"),
    # Section 2 - Discovery
    'functional_work_area': _("Functional Work Area"),
    'date_incident_detected': _("Date Incident was Detected"),
    'date_incident_occurred': _("Date Incident Occurred"),
    'time_detected': _("Time Detected"),
    'time_period_detected': _("Time Period Detected"),
    'time_occurred': _("Time Occurred"),
    'time_period_occurred': _("Time Period Occurred"),
    'individual_detected': _("Individual(s) who Detected the Incident"),
    'individual_involved': _("Individual(s) who were Involved in the Incident"),
    # Section 3 - Patient
    'patient_month_birth': _("Patient Month of Birth"),
    'patient_year_birth': _("Patient Year of Birth"),
    'patient_gender': _("Patient Gender"),
    'diagnosis': _("Diagnosis Relevant to Treatment"),
    #Section 4 - Details
    'process_step_occurred': _("Process Step where Incident Occurred"),
    'process_step_detected': _("Process Step where Incident was Detected"),
    'problem_type': _("Primary Problem Type"),
    'secondary_problem_type': _("Secondary Problem Types"),
    'contributing_factors': _("Contributing Factors"),
    'number_patients_affected': _("Number of Patients Affected"),
    'number_patients_involved': _("Number of Patients Involved"),
    # Section 5 - Treatment Delivery
    'radiation_treatment_technique': _("Radiation Treatment Technique(s)"),
    'total_dose_prescribed': _("Total Dose Prescribed (Gy)"),
    'number_fractions_prescribed': _("Number of Fractions Prescribed"),
    'number_fractions_incorrect': _("Number of Fractions Delivered Incorrectly"),
    'hardware_manufacturer_model': _("Hardware Specifications"),
    'software_manufacturer_model': _("Software Specifications"),
    'body_region_treated': _("Body Region(s) Treated"),
    'treatment_intent': _("Treatment Intent"),
    # Section 6 - Investigation
    'ameliorating_actions': _("Ameliorating Actions"),
    'safety_barriers_failed': _("Failed Safety Barriers"),
    'safety_barriers_prevented': _("Successful Safety Barriers"),
    'actions_reduce_risk': _("Actions to Reduce Risk"),
    'investigation_narrative': _("Investigation Findings and Actions Taken"),
    'narrative_by': _("Investigation Narrative By"),
    'patient_disclosure': _("Patient Disclosure"),
}

#-----------------------------------------------------------------------------------------
# Dictionary of verbose labels, with key values which are the same as fields within the
# IncidentAction model. Each verbose label provides a more readable name for the
# corresponding model field.
#-----------------------------------------------------------------------------------------
vlabel_act = {
    'action_id': _("Action ID"),
    'description_proposed': _("Action Description"),
    'responsible': _("Responsible"),
    'assigned_by': _("Assigned By"),
    'date_assigned': _("Date Assigned"),
    'complete': _("Action Complete"),
    'description_performed': _("Action Taken"),
    'completed_by': _("Completed By"),
    'date_completed': _("Date Completed"),
    'date_last_reminder': _('Date Previous Reminder Sent'),
    'first_reminder_sent': _('First Reminder Sent'),
}

#-----------------------------------------------------------------------------------------
# Abstract Models & Mixins from which other models will inherit.
#-----------------------------------------------------------------------------------------
class AbstractChoice(models.Model):
    """Skeleton for models to be accessed via Incident model FK fields.

    Abstract model from which other models within SaILS will inherit. Should be inherited
    by those models whose instances are options for any particular FK relationship with an
    Incident model instance.

    Attributes:
        name: verbose name of the option.
        slug: html friendly version of name attribute.
        description: description of the option.
        order: order in which the option is displayed in dropdown menus, etc.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True,
                            unique=True,
                            help_text=_("URL friendly version of name (only a-Z, 0-9 and _ allowed)"))
    description = models.TextField(null=True,
                                    blank=True)
    order = models.PositiveIntegerField(help_text=_("Order in which this will be displayed"))

    class Meta:
        abstract = True
        ordering = ['order', 'name']

    def __unicode__(self):
        return self.name

class StatisticsChoice(models.Model):
    """Skeleton for models/choices/filters to be accessed when generating statistics plots.

    Abstract model form which other models within SaILS will inherit. Should be inherited
    by those models whose instances are options for any ModelChoiceField in the Statistics
    form. This includes model to plot, filters (dates,completeness,etc), and so on.

    Attributes:
        name: verbose name of the option.
        slug: html friendly version of name attribute.
        description: description of the option.
        order: order in which the option is displayed in dropdown menus, etc.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True,
                            unique=True,
                            help_text=_("URL friendly version of name (only a-Z, 0-9 and _ allowed)"))
    description = models.TextField(null=True,
                                    blank=True)
    order = models.PositiveIntegerField(help_text=_("Order in which this will be displayed"),null=True, blank=True, unique=True)

    class Meta:
        abstract = True
        ordering = ['order', 'name']

    def __unicode__(self):
        return self.name


class MPTTModelMixin(object):
    """Mixin for models to be accessed via Incident model multi-multi fields.

    Mixin from which other models within SaILS will inherit. Should be inherited by those
    models whose instances are options for any particular multi-multi relationship with an
    Incident model instance.
    """
    def ancestor_names(self):
        ancestors = list(self.get_ancestors(include_self=True).values_list("name", flat=True))
        return mark_safe("&rarr;".join(ancestors))

    def ancestor_names_plain(self):
        ancestors = list(self.get_ancestors(include_self=True).values_list("name", flat=True))
        return " -> ".join(ancestors)

    def raw_save(self, *args, **kwargs):
        super(MPTTModel, self).save(*args, **kwargs)


#-----------------------------------------------------------------------------------------
# IncidentManager classes: all classes have a method to return QuerySet of (valid only!)
# incidents from the DB. Specific managers return various filtered versions of the list of
# valid incidents.
#-----------------------------------------------------------------------------------------
class IncidentManager(models.Manager):
    """Manager class to retrieve all valid incident instances.
    """
    def get_queryset(self):
        return super(IncidentManager, self).get_queryset()

    def valid(self):
        return self.get_query_set().filter(valid=True)

    def incomplete(self):
        return self.get_query_set().filter(investigation_complete=False)

    def user_all(self,user):
        return self.get_query_set().filter(investigator=user)

    def user_incomplete(self,user):
        return self.user_all(user).filter(investigation_complete=False)

class ValidIncidentManager(models.Manager):
    """Manager class to retrieve all valid incident instances.
    """
    def get_queryset(self):
        qs = super(ValidIncidentManager, self).get_queryset()
        valids = Q(valid=True)

        qs = qs.filter(valids)
        return qs

class CompleteValidIncidentManager(models.Manager):
    """Manager class to retrieve all valid, investigation-complete, incident instances.
    """
    def get_queryset(self):
        qs = super(CompleteValidIncidentManager, self).get_queryset()
        complete = Q(valid=True, investigation_complete=True)

        qs = qs.filter(complete)
        return qs

class CompleteIncidentManager(models.Manager):
    """Manager class to retrieve all investigation-complete, incident instances.
    """
    def get_queryset(self):
        qs = super(CompleteIncidentManager, self).get_queryset()
        complete = Q(valid=True, investigation_complete=True)
        invalid = Q(valid=False)

        qs = qs.filter(complete | invalid)
        return qs

class ActualIncidentManager(models.Manager):
    """Manager class to retrieve all valid, actual incident instances (not NM or RC).
    """
    def get_queryset(self):
        return super(ActualIncidentManager, self).get_queryset().filter(valid=True, reportable_circumstance=False, near_miss=False)

class IncompleteIncidentManager(models.Manager):
    """Manager class to retrieve all valid, investigation-incomplete, incident instances.
    """
    def get_queryset(self):
        return super(IncompleteIncidentManager, self).get_queryset().filter(valid=True,investigation_complete=False).exclude(investigator=None)

class IncompleteAndFlaggedIncidentManager(models.Manager):
    """Manager class to retrieve all valid, investigation-incomplete, flagged, incident instances.
    """
    def get_queryset(self):
        # Note use of Q objects in this Manager; needed for conditional logic beyond AND.
        # See use of | operator in the QuerySet to be returned
        qs = super(IncompleteAndFlaggedIncidentManager, self).get_queryset()
        incomplete = Q(valid=True, investigation_complete=False)
        flagged = Q(flag=True)

        qs = qs.filter(incomplete & flagged).exclude(investigator=None)
        return qs

class FlaggedIncidentManager(models.Manager):
    """Manager class to retrieve all valid, flagged, incident instances.
    """
    def get_queryset(self):
        # Note use of Q objects in this Manager; needed for conditional logic beyond AND.
        # See use of | operator in the QuerySet to be returned
        qs = super(FlaggedIncidentManager, self).get_queryset()
        valid = Q(valid=True)
        flagged = Q(flag=True)

        qs = qs.filter(valid & flagged).exclude(investigator=None)
        return qs

class TriageIncidentManager(models.Manager):
    """Manager class to retrieve all valid incident instances with no investigator.
    assigned
    """
    def get_queryset(self):
        return super(TriageIncidentManager, self).get_queryset().filter(valid=True, investigator=None)

#*****************************************************************************************
# @@REMOVE@@
#*****************************************************************************************
class InvestigationManager(models.Manager):
    def incomplete(self):
        return self.get_query_set().filter(complete=False)

    def user_all(self, user):
        return self.get_query_set().filter(investigator=user)

    def user_incomplete(self, user):
        return self.user_all(user).filter(complete=False)



#-----------------------------------------------------------------------------------------
# Incident model
#-----------------------------------------------------------------------------------------
class Incident(models.Model):
    """Model used to represent radiotherapy incidents in the NSIR-RT framework.

    Incident model designed to be compatible with the NSIR-RT taxonomy for classifying
    radiotherapy incidents. This model also contains a number of other fields required for
    local profiling (e.g. patient ID, oncologist, etc). Investigation status and
    parameters are also included within the incident model. Most fields which allow
    selection from a set choice list are defined via Foreign Key based fields, so the
    options may be modified with relative ease from the admin interface of SaILS or the DB
    itself.

    For a description of each attribute (each field), please see the dictionary of help
    texts defined above.
    """
    #-------------------------------------------------------------------------------------
    # Model fields, indicated by section. Each field specifies the help text, verbose
    # name, and null ability. FK based fields also indicate the class to relate to.
    #-------------------------------------------------------------------------------------
    # Local Info - not required within NSIR-RT

    predefined_type = models.ForeignKey("PredefinedIncident", help_text=help['predefined_type'], verbose_name=vlabel['predefined_type'], on_delete=models.SET_NULL, null=True, blank=True)

    event_type = models.ForeignKey("EventType", help_text=help['event_type'], verbose_name=vlabel['event_type'], null=True, blank=True)

    patient_id = models.CharField(max_length=255, help_text=help['patient_id'],verbose_name=vlabel['patient_id'],null=True,blank=True)

    submitted = models.DateTimeField(default=datetime.datetime.now, help_text=help['submitted'],verbose_name=vlabel['submitted'], null=True, blank=True)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="incident_submitted_by",help_text=help['submitted_by'],verbose_name=vlabel['submitted_by'],null=True,blank=True)

    valid = models.BooleanField(default=True, help_text=help['valid'],verbose_name=vlabel['valid'],)

    invalid_reason = models.TextField(help_text=help['invalid_reason'],verbose_name=vlabel['invalid_reason'], null=True, blank=True)

    valid_status_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="incident_valid_status_by",help_text=help['valid_status_by'],verbose_name=vlabel['valid_status_by'],null=True,blank=True)

    valid_status_date = models.DateTimeField(help_text=help['valid_status_date'],verbose_name=vlabel['valid_status_date'], null=True, blank=True)

    duplicate = models.BooleanField(default=False, help_text=help['duplicate'], verbose_name=vlabel['duplicate'],)

    duplicate_of = models.ForeignKey("self", help_text=help['duplicate_of'],verbose_name=vlabel['duplicate_of'], null=True, blank=True)

    flag = models.BooleanField(default=False,help_text=help['flag'], verbose_name=vlabel['flag'])

    discussion = models.BooleanField(default=False,help_text=help['discussion'], verbose_name=vlabel['discussion'])

    reported_by = models.CharField(max_length=255, help_text=help['reported_by'],verbose_name=vlabel['reported_by'],null=True,blank=True)

    reported_to = models.CharField(max_length=255, help_text=help['reported_to'],verbose_name=vlabel['reported_to'],null=True,blank=True)

    descriptor = models.TextField(max_length=1024, help_text=help['descriptor'],verbose_name=vlabel['descriptor'],null=True,blank=True)

    treatment_site = models.CharField(max_length=255, help_text=help['treatment_site'],verbose_name=vlabel['treatment_site'],null=True,blank=True)

    oncologist = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="incident_assigned_to_oncologist", help_text=help['oncologist'],verbose_name=vlabel['oncologist'], null=True, blank=True)
    # Previously used a FK model for oncologist selection; now just pick from SaILS users
    # who are oncologists
    #oncologist = models.ForeignKey("Oncologist", help_text=help['oncologist'],verbose_name=vlabel['oncologist'], null=True, blank=True)

    support_required = models.ForeignKey("SupportRequired", help_text=help['support_required'],verbose_name=vlabel['support_required'], null=True, blank=True, related_name="staff_support_required")

    support_given = models.ForeignKey("SupportGiven", help_text=help['support_given'],verbose_name=vlabel['support_given'], null=True, blank=True, related_name="staff_support_given")

    support_description = models.TextField(help_text=help['support_description'],verbose_name=vlabel['support_description'],blank=True)

    patient_support_required = models.ForeignKey("SupportRequired", help_text=help['patient_support_required'],verbose_name=vlabel['patient_support_required'], null=True, blank=True, related_name="patient_support_required")

    patient_support_given = models.ForeignKey("SupportGiven", help_text=help['patient_support_given'],verbose_name=vlabel['patient_support_given'], null=True, blank=True, related_name="patient_support_given")

    patient_support_description = models.TextField(help_text=help['patient_support_description'],verbose_name=vlabel['patient_support_description'],blank=True)

    # This is the unique ID associated with an incident (taken from paper form or 
    # generated during online only report.)
    incident_id = models.IntegerField(unique=True, help_text=help['incident_id'], verbose_name=vlabel['incident_id'], null=True, blank=True)

    report_type = models.ForeignKey("ReportType", help_text=help['report_type'], verbose_name=vlabel['report_type'], null=True, blank=True)

    hospital_form_id = models.CharField(max_length=255, help_text=help['hospital_form_id'],verbose_name=vlabel['hospital_form_id'],null=True,blank=True)

    coordinator_comments = models.TextField(help_text=help['coordinator_comments'],verbose_name=vlabel['coordinator_comments'],null=True,blank=True)

    # Investigation

    investigator = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="incident_assigned_to_investigator",help_text=help['investigator'],verbose_name=vlabel['investigator'],null=True,blank=True)

    investigation_assigned_date = models.DateTimeField(help_text=help['investigation_assigned_date'],verbose_name=vlabel['investigation_assigned_date'], null=True, blank=True)

    investigation_assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL,help_text=help['investigation_assigned_by'],verbose_name=vlabel['investigation_assigned_by'], null=True, blank=True)

    investigation_complete = models.BooleanField(help_text=help['investigation_complete'],verbose_name=vlabel['investigation_complete'],default=False)

    investigation_completed_date = models.DateTimeField(help_text=help['investigation_completed_date'],verbose_name=vlabel['investigation_completed_date'],null=True, blank=True)

    date_last_reminder = models.DateTimeField(help_text=help['date_last_reminder'], verbose_name=vlabel['date_last_reminder'], null=True, blank=True)

    first_reminder_sent = models.BooleanField(help_text=help['first_reminder_sent'], verbose_name=vlabel['first_reminder_sent'], default=False)

    # NSIR-RT Section 1 - Impact

    incident_description = models.TextField(help_text=help['incident_description'],verbose_name=vlabel['incident_description'],blank=True)

    reportable_circumstance = models.BooleanField(help_text=help['reportable_circumstance'],verbose_name=vlabel['reportable_circumstance'], default=False)

    near_miss = models.BooleanField(help_text=help['near_miss'],verbose_name=vlabel['near_miss'], default=False)

    acute_medical_harm = models.ForeignKey("AcuteMedicalHarm", help_text=help['acute_medical_harm'],verbose_name=vlabel['acute_medical_harm'],null=True,blank=True)

    local_severity_level = models.ForeignKey("LocalSeverityLevel", help_text=help['local_severity_level'],verbose_name=vlabel['local_severity_level'],null=True,blank=True)

    dosimetric_impact = models.ForeignKey("DosimetricImpact", help_text=help['dosimetric_impact'],verbose_name=vlabel['dosimetric_impact'],null=True,blank=True)

    latent_medical_harm = models.ForeignKey("LatentMedicalHarm", help_text=help['latent_medical_harm'],verbose_name=vlabel['latent_medical_harm'],null=True,blank=True)

    # NSIR-RT Section 2 - Discovery

    functional_work_area = models.ForeignKey("FunctionalWorkArea", help_text=help['functional_work_area'],verbose_name=vlabel['functional_work_area'],null=True,blank=True)

    date_incident_detected = models.DateField(help_text=help['date_incident_detected'],verbose_name=vlabel['date_incident_detected'],null=True,blank=True)

    date_incident_occurred = models.DateField(help_text=help['date_incident_occurred'],verbose_name=vlabel['date_incident_occurred'],null=True,blank=True)

    time_detected = models.TimeField(help_text=help['time_detected'],verbose_name=vlabel['time_detected'],null=True,blank=True)

    time_period_detected = models.ForeignKey("TimePeriodDetected", help_text=help['time_period_detected'],verbose_name=vlabel['time_period_detected'],null=True,blank=True)

    time_occurred = models.TimeField(help_text=help['time_occurred'],verbose_name=vlabel['time_occurred'],null=True,blank=True)

    time_period_occurred = models.ForeignKey("TimePeriodOccurred", help_text=help['time_period_occurred'],verbose_name=vlabel['time_period_occurred'],null=True,blank=True)

    individual_detected = models.ManyToManyField("IndividualDetected", help_text=help['individual_detected'],verbose_name=vlabel['individual_detected'],null=True,blank=True)

    individual_involved = models.ManyToManyField("IndividualInvolved", help_text=help['individual_involved'],verbose_name=vlabel['individual_involved'],null=True,blank=True)

    # NSIR-RT Section 3 - Patient
    patient_month_birth = models.ForeignKey("Month", help_text=help['patient_month_birth'],verbose_name=vlabel['patient_month_birth'],null=True,blank=True)

    patient_year_birth = models.CharField(max_length=4,help_text=help['patient_year_birth'],verbose_name=vlabel['patient_year_birth'],blank=True)

    patient_gender = models.ForeignKey("PatientGender", help_text=help['patient_gender'],verbose_name=vlabel['patient_gender'],null=True,blank=True)

    diagnosis = models.ForeignKey("Diagnosis", help_text=help['diagnosis'],verbose_name=vlabel['diagnosis'],null=True,blank=True)

    # NSIR-RT Section 4 - Details

    process_step_occurred = models.ForeignKey("ProcessStepOccurred", help_text=help['process_step_occurred'],verbose_name=vlabel['process_step_occurred'],null=True,blank=True)

    process_step_detected = models.ForeignKey("ProcessStepDetected", help_text=help['process_step_detected'],verbose_name=vlabel['process_step_detected'],null=True,blank=True)

    problem_type = TreeForeignKey("ProblemType", help_text=help['problem_type'],verbose_name=vlabel['problem_type'],null=True,blank=True)

    secondary_problem_type = TreeManyToManyField("SecondaryProblemType", help_text=help['secondary_problem_type'],verbose_name=vlabel['secondary_problem_type'],null=True,blank=True)

    contributing_factors = TreeManyToManyField("ContributingFactor", help_text=help['contributing_factors'],verbose_name=vlabel['contributing_factors'],null=True,blank=True)

    number_patients_affected = models.ForeignKey("NumberPatientsAffected", help_text=help['number_patients_affected'],verbose_name=vlabel['number_patients_affected'],null=True,blank=True)

    number_patients_involved = models.PositiveIntegerField(help_text=help['number_patients_involved'],verbose_name=vlabel['number_patients_involved'],null=True,blank=True)

    # NSIR-RT Section 5 - Treatment_Delivery

    radiation_treatment_technique = models.ForeignKey("RadiationTreatmentTechnique", related_name="rad_technique", help_text='DEPRECATED SINGLE TECHNIQUE',verbose_name='Deprecated - Single Radiation Technique',null=True,blank=True)
    radiation_treatment_techniques = models.ManyToManyField("RadiationTreatmentTechnique", related_name="rad_techniques", help_text=help['radiation_treatment_technique'],verbose_name=vlabel['radiation_treatment_technique'],null=True,blank=True)
    # @@TODO@@ may need to change max_digits for prescribed doses over 100 Gy?
    total_dose_prescribed = models.DecimalField(max_digits=4, decimal_places=2, help_text=help['total_dose_prescribed'],verbose_name=vlabel['total_dose_prescribed'], null=True,blank=True)
    
    number_fractions_prescribed = models.PositiveIntegerField(help_text=help['number_fractions_prescribed'],verbose_name=vlabel['number_fractions_prescribed'],null=True,blank=True)

    number_fractions_incorrect = models.PositiveIntegerField(help_text=help['number_fractions_incorrect'],verbose_name=vlabel['number_fractions_incorrect'],null=True,blank=True)

    hardware_manufacturer_model = models.TextField(help_text=help['hardware_manufacturer_model'],verbose_name=vlabel['hardware_manufacturer_model'],blank=True)

    software_manufacturer_model = models.TextField(help_text=help['software_manufacturer_model'],verbose_name=vlabel['software_manufacturer_model'],blank=True)

    body_region_treated = models.ManyToManyField("BodyRegionTreated", help_text=help['body_region_treated'],verbose_name=vlabel['body_region_treated'],null=True,blank=True)

    treatment_intent = models.ForeignKey("TreatmentIntent", help_text=help['treatment_intent'],verbose_name=vlabel['treatment_intent'],null=True,blank=True)

    # NSIR-RT Section 6 - Investigation

    ameliorating_actions = TreeManyToManyField("AmelioratingAction", help_text=help['ameliorating_actions'],verbose_name=vlabel['ameliorating_actions'],null=True,blank=True)

    safety_barriers_failed = TreeManyToManyField("SafetyBarrierFailed", help_text=help['safety_barriers_failed'],verbose_name=vlabel['safety_barriers_failed'],null=True,blank=True)

    safety_barriers_prevented = TreeManyToManyField("SafetyBarrierPrevented", help_text=help['safety_barriers_prevented'],verbose_name=vlabel['safety_barriers_prevented'],null=True,blank=True)

    actions_reduce_risk = TreeManyToManyField("ActionReduceRisk", help_text=help['actions_reduce_risk'],verbose_name=vlabel['actions_reduce_risk'],null=True,blank=True)
    
    investigation_narrative = models.TextField(help_text=help['investigation_narrative'],verbose_name=vlabel['investigation_narrative'],null=True,blank=True)

    narrative_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="narrative_by",help_text=help['narrative_by'],verbose_name=vlabel['narrative_by'],null=True,blank=True)

    patient_disclosure = models.BooleanField(default=False,help_text=help['patient_disclosure'], verbose_name=vlabel['patient_disclosure'])

    #-------------------------------------------------------------------------------------
    # Manager objects determine how lists of incident instances should be filtered
    #-------------------------------------------------------------------------------------
    objects = IncidentManager()
    valids = ValidIncidentManager()
    vcomplete = CompleteValidIncidentManager()
    complete = CompleteIncidentManager()
    actuals = ActualIncidentManager()
    triage = TriageIncidentManager()
    incomplete = IncompleteIncidentManager()
    incomplete_and_flagged = IncompleteAndFlaggedIncidentManager()
    flagged = FlaggedIncidentManager()

    #-------------------------------------------------------------------------------------
    # Arrays containing those fields which are required for the investigation of a
    # particular incident instance to be registered as complete. These fields differ
    # depending whether the incident is an actual incident, near miss, or reportable
    # circumstance. The NSIR-RT MDS specifieds which fields are mandatory.
    #-------------------------------------------------------------------------------------
    # @@REMOVE@@
    # unused
    complete_fields = ['incident_description','reportable_circumstance','functional_work_area','date_incident_occurred']

    req_act_fields = [
        'incident_description', 'local_severity_level','dosimetric_impact',
        'latent_medical_harm', 'functional_work_area',
        'date_incident_detected', 'time_period_detected',
        'patient_gender', 'diagnosis',
        'process_step_occurred', 'process_step_detected',
        'problem_type', 'contributing_factors',
        'number_patients_affected', 'radiation_treatment_techniques',
        'total_dose_prescribed', 'number_fractions_prescribed',
        'number_fractions_incorrect', 
        #'body_region_treated',
        'ameliorating_actions', 'safety_barriers_failed',
        'investigation_narrative',
    ]

    req_nm_fields = [
        'incident_description', 'functional_work_area',
        'date_incident_detected', 'time_period_detected',
        'diagnosis', 'process_step_occurred',
        'process_step_detected', 'problem_type',
        'contributing_factors', 'radiation_treatment_techniques',
        #'total_dose_prescribed', 'number_fractions_prescribed',
        'ameliorating_actions', 'safety_barriers_failed',
        'safety_barriers_prevented', 'investigation_narrative',
    ]

    req_rc_fields = [
        'incident_description', 'functional_work_area',
        'date_incident_detected', 'time_period_detected',
        'process_step_occurred', 'process_step_detected',
        'problem_type', 'contributing_factors',
        #'radiation_treatment_technique',
        'investigation_narrative',
    ]

    #-------------------------------------------------------------------------------------
    # Fields not shared by all event types, for each event type
    #-------------------------------------------------------------------------------------
    uncom_act_fields = [
        'patient_id', 'oncologist',
        'diagnosis',
        'acute_medical_harm', 'dosimetric_impact',
        'latent_medical_harm', 'patient_month_birth',
        'patient_year_birth', 'patient_gender',
        # 'radiation_treatment_techniques',
        'total_dose_prescribed', 'number_fractions_prescribed',
        'number_fractions_incorrect', 'body_region_treated',
        'treatment_intent'
    ]

    uncom_nm_fields = [
        'patient_id', 'oncologist',
        'diagnosis',
        'patient_month_birth', 'patient_year_birth', 
        'patient_gender',
        # 'radiation_treatment_techniques', 
        'total_dose_prescribed', 
        'number_fractions_prescribed', 'body_region_treated',
        'treatment_intent'
    ]    

    uncom_rc_fields = [
    ]

    #-------------------------------------------------------------------------------------
    # Fields not applicable to incidents involving more than one patient, for each event
    # type
    #-------------------------------------------------------------------------------------
    na_act_fields = [
        'patient_id', 'oncologist',
        'patient_month_birth', 'patient_year_birth',
        'patient_gender', 'diagnosis',
        'total_dose_prescribed', 'number_fractions_prescribed',
        'number_fractions_incorrect', 'body_region_treated',
        'treatment_intent'
    ]

    na_nm_fields = [
        'patient_id', 'oncologist',
        'patient_month_birth', 'patient_year_birth',
        'patient_gender', 'diagnosis',
        'total_dose_prescribed', 'number_fractions_prescribed',
        'number_fractions_incorrect', 'body_region_treated',
        'treatment_intent'
    ]

    #-------------------------------------------------------------------------------------
    # Fields that are mandatory according to local/institutional rules under specific
    # situations
    #-------------------------------------------------------------------------------------
    # local_mandatory_fields = [
    #     'hospital_form_id', 'patient_disclosure',
    # ]
    local_mandatory_fields = [
        {'field': 'hospital_form_id', 'dependent_field': 'local_severity_level', 'threshold': 6, 'message': 'Incidents of severity F or higher must be reported on an MUHC incident report. Please provide the form ID.'},
        {'field': 'patient_disclosure', 'dependent_field': 'local_severity_level', 'threshold': 4, 'message': 'Incidents of severity D or higher must be disclosed to the patient.'},
    ]

    #-------------------------------------------------------------------------------------
    # Array to indicate which incident model fields exhibit many-to-many relationships.
    # Is currently unused
    #-------------------------------------------------------------------------------------
    m2m_fields = [
        'individual_detected', 'individual_involved',
        'secondary_problem_type', 'contributing_factors', 
        'radiation_treatment_techniques',
        'body_region_treated', 'ameliorating_actions', 
        'safety_barriers_failed', 'safety_barriers_prevented', 
        'actions_reduce_risk', 'radiation_treatment_techniques'
    ]

    #-------------------------------------------------------------------------------------
    # Meta class
    #-------------------------------------------------------------------------------------
    class Meta:
        ordering = ("-submitted",)

    #-------------------------------------------------------------------------------------
    # Methods for the Incident model
    #-------------------------------------------------------------------------------------
    @classmethod
    def get_required_fields(cls, event_type):
        """Returns required fields as per the appropriate event type.

        Used for the template feature (application of template). When applying a template, 
        need to unfill all fields that are templatable. And if a field lost a value in this
        process, but that field is mandatory, need a way to apply "missing" highlighting.
        This method is used to serve such a purpose, see the get_field_values_view() in
        views.py.

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            missing and must be filled before the investigation can be completed.
        """
        event_type_id = EventType.objects.get(name=event_type).pk
        required_fields = None
        if event_type_id == 1:
            required_fields = cls.req_rc_fields
        elif event_type_id == 2:
            required_fields = cls.req_nm_fields
        elif event_type_id == 3:
            required_fields = cls.req_act_fields
        else:
            required_fields = cls.complete_fields

        return required_fields

    @classmethod
    def get_uncommon_fields(cls, event_type):
        """Returns fields not shared by all event types for the event type specified in 
        arguments.

        Used for the "change event type" feature on the investigation page. There many be
        fields that were previously filled, but are no longer applicable since changing
        the event type. This function is called twice to compare the fields before and
        after the event change and determine which field values need to be deleted from
        the database.

        Args:
            event_type: the PK of the event type

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            missing and must be filled before the investigation can be completed.
        """
        uncommon_fields = None
        if event_type == 1:
            uncommon_fields = cls.uncom_rc_fields
        elif event_type == 2:
            uncommon_fields = cls.uncom_nm_fields
        elif event_type == 3:
            uncommon_fields = cls.uncom_act_fields

        return uncommon_fields


    @classmethod
    def get_event_type_ids_for_field_id(cls,field_id):
        """Determine the incident event types for which the provided field_id is applicable and
        return an array of the pks of the event types.

        Currently used when counting the number of incidents considered on a particular graph
        (i.e. N). Determine if the field_id provided corresponds to a field that is applicable
        to each possible event type, and return an array of the event type ids for which the
        field is applicable.

        Args:
            field_id: A string representing a model field ID (e.g. acute_medical_harm)

        Returns:
            An array of integers corresponding to pks of EventType objects
        """
        uncom_act_fields = cls.uncom_act_fields
        uncom_rc_fields = cls.uncom_rc_fields
        uncom_nm_fields = cls.uncom_nm_fields

        applicable_event_types = [1,2,3]

        if (field_id in uncom_act_fields or field_id in uncom_nm_fields) and field_id not in uncom_rc_fields:
            applicable_event_types.remove(1)
        if (field_id in uncom_act_fields or field_id in uncom_rc_fields) and field_id not in uncom_nm_fields:
            applicable_event_types.remove(2)
        if (field_id in uncom_rc_fields or field_id in uncom_nm_fields) and field_id not in uncom_act_fields:
            applicable_event_types.remove(3)

        return applicable_event_types

    #-------------------------------------------------------------------------------------
    # Methods for Incident model instances
    #-------------------------------------------------------------------------------------
    def get_related_field_ids(self):
        """Get all field ids that relate other objects to Incidents by Foreign Key.

        Returns:
            An array of unicode strings representing the ids (non-verbose names) of all
            fields that associate other models to the Incident model via ForeignKey.
            Note does not include fields within the Incident model that points to other
            Models via ForeignKey, M2M, etc. Example is the FK field defined in the
            Subscription model that points to the Incident model.
        """
        related_fields = self._meta.get_all_related_objects()
        related_field_ids = []
        # The names from the above _meta command are, for example, notifications_nsir:subscription
        # But need to reduce to the piece to the right of the app name (i.e. just subscription)
        for related_field in related_fields:
            related_field_ids.append(related_field.name.split(":")[1])
        return related_field_ids

    def get_field_ids(self):
        """Get all field ids for the Incident model.

        Returns:
            An array of unicode strings represnting the ids (non-verbose names) of all
            fields within the Incident model. Includes FK, M2M, etc fields.
        """
        all_field_ids = self._meta.get_all_field_names()
        # Remove the related field names (e.g. subscription) from the array
        related_field_ids = self.get_related_field_ids()
        all_unrelated_field_ids = [field for field in all_field_ids if field not in related_field_ids]
        return all_unrelated_field_ids

    def get_field_verbose_names(self):
        """Get all field verbose names for the Incident model.

        Returns:
            An array of unicode strings repsenting the verbose names of all fiels within
            the Incident model. Includes FK, M2M, etc fields.
        """
        field_ids = self.get_field_ids()
        verbose_names = []
        for field_id in field_ids:
            verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
            # try:
            #     verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
            # except AttributeError:
            #     print self._meta.get_field_by_name(field_id)[0]
        return verbose_names

    def get_missing_field_ids(self):
        """Determine which NSIR-RT mandatory fields are missing and return those fields.

        Determine, based on the incident type, which NSIR-RT mandatory fields are missing
        from the current instance. Also , for additional (local) considerations, determine
        what fields are also missing that are mandatory.

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            missing and must be filled before the investigation can be completed.
        """
        missing = []
        if self.event_type.pk == 1:
            required_fields = self.req_rc_fields
        elif self.event_type.pk == 2:
            required_fields = self.req_nm_fields
        elif self.event_type.pk == 3:
            required_fields = self.req_act_fields
            # Add local mandatory fields if necessary
            # if self.acute_medical_harm != None:
            #     if self.acute_medical_harm.pk >= self.get_acute_medical_harm_threshold():
            #         required_fields = required_fields + self.get_local_mandatory_field_ids()
        else:
            required_fields = self.complete_fields

        # Add local mandatory fields if necessary
        local_m_fields = self.local_mandatory_fields
        for lfield in local_m_fields:
            if getattr(self,lfield['dependent_field']) != None:
                if getattr(self,lfield['dependent_field']).pk >= lfield['threshold']:
                    required_fields = required_fields + [lfield['field']]

        NA_fields = self.get_NA_field_ids()

        for f in required_fields:
            # Handle case of Boolean patient_disclosure field separately
            # attr holds one of the following depending on the field type:
            #   [Non-Relational text fields]:
            #       [filled]: the value of the field as unicode
            #       [unfilled]: an empty unicode string 
            #   [Non-Relational date fields]:
            #       [filled]: the Date/DateTime object representing field input
            #       [unfilled]: NoneType
            #   [FK fields]:
            #       [filled]: the model instance used to fill the field (e.g. EventType object)
            #       [unfilled]: NoneType
            #   [M2M fields]:
            #       [filled]: A ManyRelatedManager (attr.all() will give array of model instances)
            #       [unfilled]: A ManyRelatedManager (attr.all() will give an empty array)
            if f in NA_fields:
                continue
            if f == "patient_disclosure":
                if getattr(self, f) == False:
                    missing.append(f)
            else:
                attr = getattr(self, f)
                try:
                    val = attr.all()
                    # if len(val) == 0:
                    if not val:
                        missing.append(f)
                except AttributeError:
                    if attr is None or attr == "":
                        missing.append(f)

        # Add taskable actions if necessary
        action_ids = self.get_incomplete_taskable_action_ids()
        for action_id in action_ids:
            missing.append('ACTION_'+str(action_id))
        return missing

    def get_missing_field_verbose_names(self):
        """Determine which NSIR-RT mandatory fields are missing and return the verbose names
        of those fields. 

        Returns:
            An array of unicode strings repsenting the verbose names of all fields that are
            mandatory and missing. Includes FK, M2M, etc fields.
        """
        missing_field_ids = self.get_missing_field_ids()
        verbose_names = []
        for field_id in missing_field_ids:
            # There is no incident field for the missing actions, so handle those cases distinctly
            if field_id[:7] == 'ACTION_':
                verbose_names.append("Taskable Action #"+field_id[7:])
            else:
                verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
        return verbose_names

    def get_missing_field_ids_NOACTS(self):
        """Determine which NSIR-RT mandatory fields are missing and return those fields.

        Determine, based on the incident type, which NSIR-RT mandatory fields are missing
        from the current instance. Also , for additional (local) considerations, determine
        what fields are also missing that are mandatory.

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            missing and must be filled before the investigation can be completed.
        """
        missing = []
        if self.event_type.pk == 1:
            required_fields = self.req_rc_fields
        elif self.event_type.pk == 2:
            required_fields = self.req_nm_fields
        elif self.event_type.pk == 3:
            required_fields = self.req_act_fields
            # Add local mandatory fields if necessary
            # if self.acute_medical_harm != None:
            #     if self.acute_medical_harm.pk >= self.get_acute_medical_harm_threshold():
            #         required_fields = required_fields + self.get_local_mandatory_field_ids()
        else:
            required_fields = self.complete_fields

        # Add local mandatory fields if necessary
        local_m_fields = self.local_mandatory_fields
        for lfield in local_m_fields:
            if getattr(self,lfield['dependent_field']) != None:
                if getattr(self,lfield['dependent_field']).pk >= lfield['threshold']:
                    required_fields = required_fields + [lfield['field']]

        NA_fields = self.get_NA_field_ids()

        for f in required_fields:
            # Handle case of Boolean patient_disclosure field separately
            # attr holds one of the following depending on the field type:
            #   [Non-Relational text fields]:
            #       [filled]: the value of the field as unicode
            #       [unfilled]: an empty unicode string 
            #   [Non-Relational date fields]:
            #       [filled]: the Date/DateTime object representing field input
            #       [unfilled]: NoneType
            #   [FK fields]:
            #       [filled]: the model instance used to fill the field (e.g. EventType object)
            #       [unfilled]: NoneType
            #   [M2M fields]:
            #       [filled]: A ManyRelatedManager (attr.all() will give array of model instances)
            #       [unfilled]: A ManyRelatedManager (attr.all() will give an empty array)
            if f in NA_fields:
                continue
            if f == "patient_disclosure":
                if getattr(self, f) == False:
                    missing.append(f)
            else:
                attr = getattr(self, f)
                try:
                    val = attr.all()
                    # if len(val) == 0:
                    if not val:
                        missing.append(f)
                except AttributeError:
                    if attr is None or attr == "":
                        missing.append(f)

        return missing

    def is_complete(self):
        """Determine if the current incident has been completed or not based on whether
        or not there are missing mandatory fields; does NOT depend if the incident
        has investigation_complete=True.

        Returns:
            A Boolean value indicating whether or not the investigation for the current
            incident has been completed (True if complete, False if not)
        """
        if len(self.get_missing_field_ids()) == 0:
            return True
        else:
            return False

    def get_reported_field_ids(self):
        """Return array of fields which should be included in the initial report.

        This function is used in preparing the Investigation forms (RC, NM, ACT) by
        providing the field ids (non verbose names) that were included in the initial
        report and are included in the investigation; but should not be able to be
        changed during the investigation (i.e. are immutable). 

        Returns:
            An array of field names (not verbose names, exact model field names) which
            should be included in the initial report of an incident, conditional on the
            type of event it is.
        """
        reported_fields = [
            'report_type', 'reported_by',
            'reported_to', 'submitted_by',
            'submitted', 'descriptor',
            'incident_description', 'event_type',
            'functional_work_area', 'date_incident_detected',
            'time_period_detected', 'number_patients_involved',
            'coordinator_comments'
        ]
           
        if self.event_type.pk == 2:
            additional_fields = [
                'patient_id', 'oncologist',
                'diagnosis',
                'body_region_treated'
            ]
            reported_fields = reported_fields + additional_fields
        elif self.event_type.pk == 3:
            additional_fields = [
                'patient_id', 'oncologist',
                'diagnosis',
                'body_region_treated'
            ]
            reported_fields = reported_fields + additional_fields

        return reported_fields

    def get_reported_field_verbose_names(self):
        """Determine which fields were included in the initial report and return the
        verbose names of those fields.

        Returns:
            An array of unicode strings repsenting the verbose names of all fields
            in the initial incident report. Includes FK, M2M, etc fields.
        """
        reported_field_ids = self.get_reported_field_ids()
        verbose_names = []
        for field_id in reported_field_ids:
            verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
        return verbose_names

    def get_NA_field_ids(self):
        """Determine investigation fields that are not applicable to the current incident,
        if it involves more than 1 patient.

        Which fields are not applicable depends on the event type

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            not applicable to the incident because it involves more than one patient.    
        """
        NA_fields = []

        if self.number_patients_involved > 1:
            if self.event_type.pk == 2:
                NA_fields = self.na_nm_fields
            elif self.event_type.pk == 3:
                NA_fields = self.na_act_fields

        return NA_fields

    def get_NA_field_verbose_names(self):
        """Determine verbose names of investigation fields that are not applicable to the 
        current incident, if it involves more than 1 patient.

        Returns:
            An array of unicode strings repsenting the verbose names of all fields
            that are not applicable for incidents involving more than 1 patient. 
            Includes FK, M2M, etc fields.
        """
        NA_field_ids = self.get_NA_field_ids()
        verbose_names = []
        for field_id in NA_field_ids:
            verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
        return verbose_names

    def get_local_mandatory_field_ids(self):
        """Determine investigation fields that are mandatory according to local/institutional
        guidelines (In addition to NSIR-RT).

        Additional fields may be required (mandatory) to complete an investigation, but
        vary depending on the centre/province/etc. Current implementation returns fields
        that are mandatory as per local legislation for incidents above a severity threshold.
        Note that the conditions in which these are mandatory are not specified here,
        rather this method is called when those conditions have already been triggered.

        Returns:
            An array of field names (not verbose names, exact model field names) which are
            mandatory according to local/institutional rules.  
        """
        local_field_dicts = self.local_mandatory_fields
        local_fields = []
        for field_dict in local_field_dicts:
            local_fields.append(field_dict['field'])

        return local_fields

    def get_local_mandatory_field_verbose_names(self):
        """Determine verbose names of investigation fields that are mandatory according 
        to local/institutional guidelines (In addition to NSIR-RT).

        Returns:
            An array of unicode strings repsenting the verbose names of all fields
            that are not mandatory according to local rules.
        """
        local_mandatory_field_ids = self.get_local_mandatory_field_ids()
        verbose_names = []
        for field_id in local_mandatory_field_ids:
            verbose_names.append(self._meta.get_field_by_name(field_id)[0].verbose_name)
        return verbose_names

    def get_local_mandatory_field_dicts(self):
        """Provide an array of dictionaries containing pertinent information for all investigation
        form fields that are mandatory according to local policy

        Returns:
            An array of dictionaries containing the information for local mandatory fields.
            Dictionary elements include: the locally required field, the field upon which
            it depends, the threshold value of that field above which the locally required
            field is mandatory, and a message to be displayed to the user when the threshold
            is exceeded. 
        """
        return self.local_mandatory_fields

    def get_local_mandatory_field_html_ids(self):
        """Determine HTML field IDs of investigation fields that are mandatory according 
        to local/institutional guidelines (In addition to NSIR-RT).

        Returns:
            An array of unicode strings repsenting the HTML field IDs of all fields
            that are not mandatory according to local rules.
        """
        local_mandatory_field_ids = self.get_local_mandatory_field_ids()
        html_ids = []
        for field_id in local_mandatory_field_ids:
            html_ids.append("#id_"+field_id)
        return html_ids

    def get_acute_medical_harm_threshold(self):
        """Determine the PK of the option for acute_medical_harm above which disclosure
        is required.

        Returns:
            An integer value representing the PK of an AcuteMedicalHarm object.
        """
        threshold = 2 # PK for AcuteMedicalHarm = Minor
        return threshold


    # UNUSED!!
    def get_m2m_fields(self): 
        """Return array of many-to-many fields in the incident model.

        Return array of many-to-many fields in the incident model

        Returns:
            An array of field names (not verbose names, exact model field names) which
            exhibit many-to-many relationships with another model type
        """
        m2ms = []

        for f in self.m2m_fields:
            m2ms.append(f)

        return m2ms

    def get_incomplete_taskable_action_ids(self):
        """Determine if there are any taskable actions for an incident, and return an array
        of integer action ID numbers accordingly.

        Note thatthe action ID numbers are just integers starting at 1 and incrementing by
        1 for each action of the same investigation.

        Returns:
            An array of integers representing the action IDs of all actions associated
            with the current incident.
        """
        actions = IncidentAction.objects.filter(
            Q(incident=self),
            Q(complete=False)
        ).values_list('action_id', flat=True)
        return actions

    #=====================================================================================
    # Returns the list of actions which have been designated as a response to this Incident
    # @@REMOVE@@
    #=====================================================================================
    def get_actions(self):
        return IncidentAction.objects.all().filter(incident=self)

    def complete_fields_set(self):
        """Returns Boolean response indicating whether there are any missing fields to 
        label in order to label the incident as Complete.
        """
        return len(self.get_missing_field_ids()) == 0


    def save(self, *args, **kwargs):
        """Save current field inputs for the Incident object, in the DB.
        """

        #@@REMOVE@@
        # Use this to set reportable_circumstance vs. near_miss fields
        # if self.event_type.pk == 1:
        #     self.reportable_circumstance = True
        # else:
        #     self.reportable_circumstance = False

        # if self.event_type.pk == 2:
        #     self.near_miss = True
        # else:
        #     self.near_miss = False

        super(Incident, self).save(*args, **kwargs)

        #@@REMOVE@@
        # Is currently creating an investigation object for each incident upon first save
        # of that incident. But do not use that investigation object at all currently.
        try:
            self.investigation
        except Investigation.DoesNotExist:
            self.investigation = Investigation.objects.create(incident=self)

        if not self.valid:
            self.investigation.complete = True
            self.investigation.save()

    def get_absolute_url(self):
        """Returns absolute URL for current incident using its incident_id (not primary 
        key!).
        """
        return reverse('incidents_nsir:incident', kwargs={"incident_id": self.incident_id})

    #=====================================================================================
    # @@TODO@@ implement this correctly using event_type field (so don't have to check
    # by event type pk outside of this model)
    #=====================================================================================
    def is_near_miss(self):
        """Indicate whether Incident is a near miss or not.
        """
        return self.near_miss == True

    #=====================================================================================
    # @@TODO@@ implement this correctly using event_type field (so don't have to check
    # by event type pk outside of this model)
    #=====================================================================================
    def is_reportable_circumstance(self):
        """Indicate whether Incident is a reportable circumstance or not.
        """
        return self.reportable_circumstance == True

    def __unicode__(self):
        """Return unicode (~string) definition of the current Incident object.
        """
        return "Incident(%d, %s)" % (self.incident_id, self.incident_description)


#*****************************************************************************************
# @@REMOVE@@
# InvestigationManager class: has methods to return QuerySet of investigations from the
# DB. Specific methods return various filtered versions of the completed list of
# investigation instances
#*****************************************************************************************
class InvestigationManager(models.Manager):
    def incomplete(self):
        return self.get_query_set().filter(complete=False)

    def user_all(self, user):
        return self.get_query_set().filter(investigator=user)

    def user_incomplete(self, user):
        return self.user_all(user).filter(complete=False)

#*****************************************************************************************
# @@REMOVE@@
# Investigation model
#*****************************************************************************************
class Investigation (models.Model):
    incident = models.OneToOneField(Incident)

    #investigator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="investigations", null=True, blank=True)
    assigned = models.DateTimeField(verbose_name=_("Date Investigator Assigned"), null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="incidents_assigned", null=True, blank=True)

    complete = models.BooleanField(default=False)
    completed = models.DateTimeField(null=True, blank=True)

    # @@TODO@@ Fill in when know which fields are mandatory (See taxonomy - may have
    # additional fields which are mandatory for local investigation as well)
    complete_fields = ["investigator"]

    #=====================================================================================
    # Returns an array of the fields which are not yet filled, which are required for the
    # Investigation object to be annotated as "Complete"
    #=====================================================================================
    def missing_fields(self):
        inv_fields = [f for f in self.complete_fields if not getattr(self, f)]
        inc_fields = self.incident.get_missing_field_ids()

        #@@TODO@@ add conditionals to add extra required fields depending on type of
        # incident linked to the investigation

        inc_fields = ["incident__%s" % f for f in inc_fields]
        return inv_fields + inc_fields

    #=====================================================================================
    # Return the values for the fields required to be filled.
    #=====================================================================================
    def complete_fields_set(self):
        return all([getattr(self, f) for f in self.complete_fields])

    #=====================================================================================
    # Returns a Boolean value indicating whether the required fields are filled in or not.
    # Invalid incidents do not have requried fields.
    #=====================================================================================
    def required_complete(self):

        if not self.incident.valid:
            return True

        has_required_fields = self.complete_fields_set() and self.incident.complete_fields_set()

        return has_required_fields

#-----------------------------------------------------------------------------------------
# @@REMOVE@@
# This receiver will cause this function to execute upon any deletion of an Investigation
# object. Deletes the corresponding incident as well.
#-----------------------------------------------------------------------------------------
# @receiver(post_delete, sender=Investigation)
# def post_delete_investigation(sender, instance, *args, **kwargs):
#     if instance.incident:  # just in case user is not specified
#         instance.incident.delete()


#-----------------------------------------------------------------------------------------
# Incident Action model
#-----------------------------------------------------------------------------------------
class IncidentAction(models.Model):
    """Model used to represent taskable actions assigned for a particular
    incident/investigation.

    For a description of each attribute (each field), please see the dictionary of help
    texts defined above.
    """
    class Meta:
        verbose_name_plural = _("Actions")

    incident = models.ForeignKey(Incident)

    action_id = models.IntegerField(help_text=help_act['action_id'], verbose_name=vlabel_act['action_id'], null=True, blank=True)

    description_proposed = models.TextField(help_text=help_act['description_proposed'],verbose_name=vlabel_act['description_proposed'],blank=True,null=True)

    responsible = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="user_responsible_action", help_text=help_act['responsible'], verbose_name=vlabel_act['responsible'],null=True,blank=True)

    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="user_assigned_action", help_text=help_act['assigned_by'], verbose_name=vlabel_act['assigned_by'],null=True,blank=True)

    date_assigned = models.DateTimeField(help_text=help_act['date_assigned'],verbose_name=vlabel_act['date_assigned'],null=True, blank=True)

    complete = models.BooleanField(help_text=help_act['complete'],verbose_name=vlabel_act['complete'],default=False)

    description_performed = models.TextField(help_text=help_act['description_performed'],verbose_name=vlabel_act['description_performed'],default="",blank=True,null=True)

    completed_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="user_completed_action", help_text=help_act['completed_by'], verbose_name=vlabel_act['completed_by'],null=True,blank=True)

    date_completed = models.DateTimeField(help_text=help_act['date_completed'],verbose_name=vlabel_act['date_completed'],null=True, blank=True)

    date_last_reminder = models.DateTimeField(help_text=help['date_last_reminder'], verbose_name=vlabel['date_last_reminder'], null=True, blank=True)

    first_reminder_sent = models.BooleanField(help_text=help['first_reminder_sent'], verbose_name=vlabel['first_reminder_sent'], default=False)

#-----------------------------------------------------------------------------------------
# This receiver will cause this function to execute upon any deletion of an IncidentAction
# object. Is required to delete all the comments associated with an IncidentAction object
# which are not explicitly tied to the object.
#-----------------------------------------------------------------------------------------
# @receiver(post_delete, sender=IncidentAction)
# def incidentaction_delete(sender, instance, **kwargs):
#     # Pass false so FileField doesn't save the model.
#     content = ContentType.objects.get(name="incident action")
#     comments = Comment.objects.filter(content_type=content.id, object_pk=instance.pk)
#     for comment in comments:
#         comment.delete()


#*****************************************************************************************
# @@REMOVE@@
# Sharing Actions
#*****************************************************************************************
#-----------------------------------------------------------------------------------------
# Model for the various SharingAudiences
# The choices available for this model are filled by one of the .JSON fixtures located
# currently at fixtures/sharingaudience.json. These have reference to this model.
#-----------------------------------------------------------------------------------------
class SharingAudience(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = _("Sharing Audience")
        verbose_name_plural = _("Sharing Audiences")

#-----------------------------------------------------------------------------------------
# This model should be instanced for all sharing goals for a particular incident. All
# IncidentSharing objects should be linked to a specific Incident object. Defines an
# audience for the incident to be shared with, a user responsible for sharing the incident,
# and also a Boolean indicating whether or not it has yet been shared.
#-----------------------------------------------------------------------------------------
class IncidentSharing(models.Model):
    class Meta:
        verbose_name_plural = _("Sharing")

    incident = models.ForeignKey(Incident)

    sharing_audience = models.ForeignKey(SharingAudience)

    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="incidentsharing", null=True)

    assigned = models.DateTimeField(null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="incidentsharing_assigned")

    done = models.BooleanField(default=False)
    done_date = models.DateTimeField(null=True, blank=True)

#-----------------------------------------------------------------------------------------
# This receiver will cause this function to execute upon any deletion of an IncidentSharing
# object. Is required to delete all the comments associated with an IncidentSharing object
# which are not explicitly tied to the object.
#-----------------------------------------------------------------------------------------
# @receiver(post_delete, sender=IncidentSharing)
# def incidentsharing_delete(sender, instance, **kwargs):
#     # Pass false so FileField doesn't save the model.
#     content = ContentType.objects.get(name="incident sharing")
#     comments = Comment.objects.filter(content_type=content.id, object_pk=instance.pk)
#     for comment in comments:
#         comment.delete()


#-----------------------------------------------------------------------------------------
# Taxonomy specific classes, which relate to the Incident model via key based
# relationships. Please see the dicitionary of help texts provided above for description
# of what each class type is meant to represent within the NSIR-RT framework. Plural
# verbose names are provided here at the class level.
#-----------------------------------------------------------------------------------------
# Local Info

class EventType(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "event type"
        verbose_name_plural = "event types"

#@@REMOVE@@
class Oncologist(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True,
                            unique=True,
                            help_text=_("URL friendly version of name (only a-Z, 0-9 and _ allowed)"))
    description = models.TextField(null=True,
                                    blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        #ordering = ('order',)
        ordering = ['last_name', 'first_name']

    def __unicode__(self):
        return "Dr. " + self.first_name + " " + self.last_name

class SupportRequired(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "Staff support required"
        verbose_name_plural = "support required choices"

class SupportGiven(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "staff support provided"
        verbose_name_plural = "support given choices"

class ReportType(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "type of report"
        verbose_name_plural = "types of initial incident reports"

# NSIR-RT Section 1 - Impact

class AcuteMedicalHarm(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        #ordering = ('order',)
        verbose_name = "acute medical harm"
        verbose_name_plural = "acute medical harm choices"

# The following field was added to accomodate institutionl/municipal severity
# levels and thresholds. Instances of this class (i.e. available options) will
# likely differ from one institution to the next.
class LocalSeverityLevel(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "acute incident severity"
        verbose_name_plural = "local severity level choices"

class DosimetricImpact(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "dosimetric impact"
        verbose_name_plural = "dosimetric impacts"

class LatentMedicalHarm(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "latent medical harm"
        verbose_name_plural = "latent medical harm choices"

# NSIR-RT Section 2 - Discovery

class FunctionalWorkArea(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "functional work area"
        verbose_name_plural = "functional work areas"

class TimePeriodDetected(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "time period incident was detected"
        verbose_name_plural = "time periods (detected)"

class TimePeriodOccurred(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "time period incident occurred"
        verbose_name_plural = "time periods (occurred)"

class IndividualDetected(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "individual who detected the incident"
        verbose_name_plural = "individuals (detected)"

class IndividualInvolved(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "individual involved in the incident"
        verbose_name_plural = "individuals (involved)"

# NSIR-RT Section 3 - Patient

class Month(AbstractChoice):
    abbrev = models.CharField(max_length=255, null=True, blank=True)

    class Meta(AbstractChoice.Meta):
        verbose_name_plural = "months"

class PatientGender(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "patient gender"
        verbose_name_plural = "patient genders"

class Diagnosis(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "patient diagnosis"
        verbose_name_plural = "diagnoses"

# NSIR-RT Section 4 - Details

class ProcessStepOccurred(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "process step where incident occurred"
        verbose_name_plural = "process steps where incident occurred"

class ProcessStepDetected(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "process step where incident detected"
        verbose_name_plural = "process steps where incident detected"

class ProblemType(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the problem type parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "primary problem type"
        verbose_name_plural = "primary problem types"

class SecondaryProblemType(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the problem type parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "secondary problem type"
        verbose_name_plural = "secondary problem types"

class ContributingFactor(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the contributing factor parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "contributing factor"
        verbose_name_plural = "contributing factors"

class NumberPatientsAffected(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "number of patients affected"
        verbose_name_plural = "number of patients affected"

# NSIR-RT Section 5 - Treatment Delivery

class RadiationTreatmentTechnique(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "radiation treatment technique"
        verbose_name_plural = "radiation treatment techniques"

class BodyRegionTreated(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "body region treated"
        verbose_name_plural = "body regions treated"

class TreatmentIntent(AbstractChoice):
    class Meta(AbstractChoice.Meta):
        verbose_name = "treatment intent"
        verbose_name_plural = "treatment intents"

# NSIR-RT Section 6 - Investigation

class AmelioratingAction (MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the action parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "ameliorating action"
        verbose_name_plural = "ameliorating actions"

class SafetyBarrierFailed(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the safety barrier parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "safety barrier that failed"
        verbose_name_plural = "safety barriers that failed to prevent incident"

class SafetyBarrierPrevented(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the safety barrier parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "safety barrier that caught the incident"
        verbose_name_plural = "safety barriers that prevented the incident"

class ActionReduceRisk(MPTTModelMixin, MPTTModel, AbstractChoice):
    parent = TreeForeignKey('self',
                            blank=True,
                            null=True,
                            related_name="children",
                            help_text=_("If this is a sub-classification choose the action parent class"))
    class Meta(AbstractChoice.Meta):
        verbose_name = "action to reduce risk"
        verbose_name_plural = "actions to reduce risk"


class StatPlotType(StatisticsChoice):
    type_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- plot types"

class StatParameterType(StatisticsChoice):
    type_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- plotting parameter types"

class StatDateType(StatisticsChoice):
    field_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- date types"

class StatUserChoice(StatisticsChoice):
    account_field_name = models.CharField(max_length=255, null=True, blank=True)
    incident_field_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- user type choices"

class StatFKModelChoice(StatisticsChoice):
    model_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- fk model choices"

class StatCompletionFilter(StatisticsChoice):
    filter_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- completion status filters"

class StatDateBin(StatisticsChoice):
    bin_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta(StatisticsChoice.Meta):
        verbose_name_plural = "statistics- date bins"



class PredefinedIncident(models.Model):
    """Model used to represent a template for a predefined incident type.
    """
    name = models.CharField(
        max_length=255,
        help_text = "Verbose name of the predefined incident type",
        verbose_name = 'Name of the Template',
        unique=True
    )
    code_name = models.CharField(
        max_length=255,
        help_text = "Code name of the predefined incident type"
    )
    description = models.TextField(
        help_text = "Please briefly describe the nature of the template being saved",
        verbose_name = "Description of the Template",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="predefined_created_by",
        help_text="User who created this predefined incident template",
    )

    def __unicode__(self):
        return self.name


class PredefinedField(models.Model):
    """Model used to represent a filled field (field name, value pair) associated with a
    particular predefiend incident type.
    """
    model_field = models.ForeignKey("AllowedTemplateField",
        help_text = "Key to the object representing an incident model field, for which this predefined field will fill"
    )
    field_value = models.PositiveIntegerField(
        help_text = "The pk of the choice with which the field specified in model_field should be filled"
    )
    incident_type = models.ForeignKey(
        "PredefinedIncident",
        help_text = "FK to the PredefinedIncident model instance for which this field/value pair is associated"
    )
    def __unicode__(self):
        return "[%s] %s:%s" % (self.incident_type,self.model_field,self.field_value)


class AllowedTemplateField(models.Model):
    """Model used to identify fields which are to be included in templates of predefined
    incident types.
    """
    field_name = models.CharField(
        max_length=255,
        help_text = "Name of the Incident model field that may have its value stored in a template"
    )
    event_type = models.ManyToManyField(
        "EventType",
        help_text = "Event types for which this field may be used as a template"
    )

    class Meta:
        ordering = ['field_name',]

    def __unicode__(self):
        return self.field_name

class IncidentImage(models.Model):
    """Model used to represent an image that can be uploaded to a particular incident
    investigation.
    """
    incident = models.ForeignKey(Incident)

    image_name = models.CharField(
        max_length = 255,
        help_text = "Name/title of the image, to be displayed",
        verbose_name = "Image Name",
    )

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name="user_uploaded_image", 
    )

    uploaded_date = models.DateTimeField(
    )

    image = models.ImageField(
        upload_to = 'incidentimages/',
        help_text = "The image file to be uploaded",
        verbose_name = "Image File"
    )

    class Meta:
        ordering = ['image_name', 'uploaded_date']

    def __unicode__(self):
        return self.image_name