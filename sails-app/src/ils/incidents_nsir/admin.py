from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin
from adminsortable.admin import SortableAdminMixin
from import_export.admin import ExportMixin

from . import models

class IncidentAdmin(admin.ModelAdmin):
    """Handle admin page for incident instances.
    """
    # fieldsets = [
    #     ('Local Info', {'fields': ['incident_id' , 'report_type', 'event_type', 'patient_id', 'submitted', 'submitted_by', 'valid', 'duplicate', 'duplicate_of', 'flag', 'reported_by', 'reported_to', 'descriptor', 'treatment_site', 'oncologist', 'support_required', 'support_given', 'support_description']}),
    #     ('Investigation', {'fields': ['investigator', 'investigation_assigned_date', 'investigation_assigned_by', 'investigation_complete', 'investigation_completed_date']}),
    #     ('1 - Impact', {'fields': ['incident_description', 'reportable_circumstance', 'near_miss', 'acute_medical_harm', 'dosimetric_impact', 'latent_medical_harm']}),
    #     ('2 - Discovery', {'fields': ['functional_work_area', 'date_incident_detected', 'date_incident_occurred', 'time_period_detected', 'time_period_occurred', 'individual_detected', 'individual_involved']}),
    #     ('3 - Patient', {'fields': ['patient_month_birth', 'patient_year_birth', 'patient_gender', 'diagnosis']}),
    #     ('4 - Details', {'fields': ['process_step_occurred', 'process_step_detected', 'problem_type', 'secondary_problem_type', 'contributing_factors', 'number_patients_affected']}),
    #     ('5 - Treatment Delivery', {'fields': ['radiation_treatment_technique', 'total_dose_prescribed', 'number_fractions_prescribed', 'number_fractions_incorrect', 'hardware_manufacturer_model', 'software_manufacturer_model', 'body_region_treated', 'treatment_intent']}),
    #     ('6 - Investigation', {'fields': ['ameliorating_actions', 'safety_barriers_failed', 'safety_barriers_prevented', 'actions_reduce_risk']})
    # ]
    fieldsets = [
        ('Local Follow-up', {'fields': ['investigator','flag','discussion','hospital_form_id']}),
        ('Reported Information', {'fields': ['report_type','reported_by','reported_to','submitted_by','submitted','patient_id','oncologist','treatment_site','descriptor']}),
        ('Investigation Specifics', {'fields': ['investigation_assigned_date', 'investigation_assigned_by', 'investigation_complete', 'investigation_completed_date']}),
        ('NSIR-RT Section 1 - Impact', {'fields': ['incident_description', 'coordinator_comments', 'event_type', 'acute_medical_harm', 'local_severity_level', 'dosimetric_impact', 'latent_medical_harm']}),
        ('NSIR-RT Section 2 - Discovery', {'fields': ['functional_work_area', 'date_incident_detected', 'date_incident_occurred', 'time_period_detected', 'time_period_occurred', 'individual_detected', 'individual_involved']}),
        ('NSIR-RT Section 3 - Patient', {'fields': ['patient_month_birth', 'patient_year_birth', 'patient_gender', 'diagnosis']}),
        ('NSIR-RT Section 4 - Details', {'fields': ['process_step_occurred', 'process_step_detected', 'problem_type', 'secondary_problem_type', 'contributing_factors', 'number_patients_involved', 'number_patients_affected']}),
        ('NSIR-RT Section 5 - Treatment Delivery', {'fields': ['radiation_treatment_techniques', 'total_dose_prescribed', 'number_fractions_prescribed', 'number_fractions_incorrect', 'hardware_manufacturer_model', 'software_manufacturer_model', 'body_region_treated', 'treatment_intent']}),
        ('NSIR-RT Section 6 - Investigation', {'fields': ['investigation_narrative','ameliorating_actions', 'safety_barriers_failed', 'safety_barriers_prevented', 'actions_reduce_risk']}),
        ('Support', {'fields': ['support_required','support_given','support_description','patient_support_required','patient_support_given','patient_support_description']})
    ]

    list_display = ('incident_id','event_type','submitted','investigator','investigation_complete','descriptor')
    list_filter = ['event_type', 'investigator', ]
    search_fields = ['incident_description', 'descriptor']

    def make_complete(self, request, queryset):
        rows_updated = queryset.update(investigation_complete=True)
        if rows_updated == 1:
            message_bit = "1 Incident was"
        else:
            message_bit = "%s Incidents were" % rows_updated
        self.message_user(request, "%s successfully marked as complete." % message_bit)
    make_complete.short_description = "Make selected investigations complete"

    actions = [make_complete]



class IncidentActionAdmin(admin.ModelAdmin):
    """Handle admin page for IncidentAction instances
    """
    fieldsets = [
        ('Base Info', {'fields':['incident','action_id']}),
        ('Assigned Info', {'fields':['description_proposed','responsible','assigned_by','date_assigned']}),
        ('Completed Info', {'fields':['complete','description_performed','completed_by','date_completed']})
    ]
    list_display = ('id','incident_id','action_id','description_proposed')

    def incident_id(self,instance):
        return instance.incident.incident_id

#-----------------------------------------------------------------------------------------
# Following two classes are used for admin display of models without tree structure.
#-----------------------------------------------------------------------------------------
class NameSlugAdminMixin(object):
    prepopulated_fields = {"slug": ("name",)}
    pass

class NameSlugAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'description','order']

# Contains models to be registered to Admin site via the NameSlugAdmin
nameslug_array = [
    models.ReportType,
    models.EventType,
    models.AcuteMedicalHarm,
    models.LocalSeverityLevel,
    models.DosimetricImpact,
    models.LatentMedicalHarm,
    models.FunctionalWorkArea,
    models.TimePeriodDetected,
    models.TimePeriodOccurred,
    models.IndividualDetected,
    models.IndividualInvolved,
    models.PatientGender,
    models.Diagnosis,
    models.ProcessStepOccurred,
    models.ProcessStepDetected,
    models.NumberPatientsAffected,
    models.RadiationTreatmentTechnique,
    models.BodyRegionTreated,
    models.TreatmentIntent,
    models.SupportRequired,
    models.SupportGiven,
]

class MonthAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'abbrev', 'description', 'order']

#-----------------------------------------------------------------------------------------
# Define admin interface for displaying models with tree-like hierarchies
#-----------------------------------------------------------------------------------------
class MPTTModelAdmin(DjangoMpttAdmin):
    list_display = ("name", "parent", "lft", "rght", "level", "tree_id",)
    prepopulated_fields = {"slug": ("name",)}

# Contains models to be registered to Admin site via the MPTTModelAdmin
mpttmodel_array = [
    models.ProblemType,
    models.SecondaryProblemType,
    models.ContributingFactor,
    models.AmelioratingAction,
    models.SafetyBarrierFailed,
    models.SafetyBarrierPrevented,
    models.ActionReduceRisk
]

#-----------------------------------------------------------------------------------------
# Following classes are used for admin display of statistics models
#-----------------------------------------------------------------------------------------
class StatisticsNameSlugAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'description','order']

# Contains models to be registered to Admin site via the NameSlugAdmin
statistics_array = [
]

class StatisticsPlotTypeAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'type_name', 'description', 'order']

class StatisticsParameterTypeAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'type_name', 'description', 'order']

class StatisticsDateAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'field_name', 'description', 'order']

class StatisticsUserAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'account_field_name', 'incident_field_name', 'description', 'order']

class StatisticsFKModelAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'model_name', 'description', 'order']

class StatisticsCompletionFilterAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'filter_name', 'description', 'order']

class StatisticsDateBinAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'bin_name', 'description', 'order']

#-----------------------------------------------------------------------------------------
# Following classes are used for admin display of models used in thetemplate/predefined 
# feature of SaILS
#-----------------------------------------------------------------------------------------

class PredefinedIncidentAdmin(admin.ModelAdmin):
    fields = ['name', 'code_name', 'description', 'created_by']
    list_display = ('__unicode__','code_name')

class PredefinedFieldAdmin(admin.ModelAdmin):
    fields = ['model_field', 'field_value', 'incident_type']
    list_display = ('__unicode__','incident_type','model_field','field_value')
    list_filter = ['incident_type']

class AllowedTemplateFieldAdmin(admin.ModelAdmin):
    fields = ['field_name','event_type']
    list_filter = ['event_type']

class IncidentImageAdmin(admin.ModelAdmin):
    fields = ['incident', 'image_name', 'uploaded_by', 'uploaded_date', 'image']
    search_fields = ['incident__pk']

    list_display = ('image_name','incident_id','uploaded_by','uploaded_date')

    def incident_id(self,instance):
        return instance.incident.incident_id

admin.site.register(nameslug_array,NameSlugAdmin)
admin.site.register(mpttmodel_array, MPTTModelAdmin)
admin.site.register(statistics_array,StatisticsNameSlugAdmin)
admin.site.register(models.Incident, IncidentAdmin)
admin.site.register(models.Month, MonthAdmin)
admin.site.register(models.IncidentAction, IncidentActionAdmin)
admin.site.register(models.StatPlotType, StatisticsPlotTypeAdmin)
admin.site.register(models.StatParameterType, StatisticsParameterTypeAdmin)
admin.site.register(models.StatDateType, StatisticsDateAdmin)
admin.site.register(models.StatUserChoice, StatisticsUserAdmin)
admin.site.register(models.StatFKModelChoice, StatisticsFKModelAdmin)
admin.site.register(models.StatCompletionFilter, StatisticsCompletionFilterAdmin)
admin.site.register(models.StatDateBin, StatisticsDateBinAdmin)
admin.site.register(models.PredefinedIncident, PredefinedIncidentAdmin)
admin.site.register(models.PredefinedField, PredefinedFieldAdmin)
admin.site.register(models.AllowedTemplateField, AllowedTemplateFieldAdmin)
admin.site.register(models.IncidentImage, IncidentImageAdmin)