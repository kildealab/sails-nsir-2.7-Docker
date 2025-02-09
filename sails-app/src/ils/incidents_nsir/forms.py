from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth import authenticate, get_user_model
from django.forms.models import modelformset_factory
from django.forms.widgets import Select, SelectMultiple, HiddenInput
from django.forms.util import flatatt
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.html import escape, conditional_escape, mark_safe, format_html
from django.utils.translation import ugettext as _
from ils.utils import get_users_by_permission

from accounts.models import ILSUser
from mptt.forms import TreeNodeChoiceField, TreeNodeMultipleChoiceField

import datetime
import models

# For CustomPasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.contrib.sites.models import get_current_site
from django.utils.encoding import force_bytes


User = get_user_model()
REMOVE_HELP_MESSAGE = unicode(_('Hold down "Control", or "Command" on a Mac, to select more than one.'))

# help dictionary was needed for previous implementation of m2m fields; do not think is 
# used now
help = {
    'secondary_problem_type': _('Additional problems that describe the occurrence of the incident.'),
    'contributing_factors': _("A circumstance, action or influence which is thought to have played a part in the origin or development of an incident or to have increased the risk of an incident."),
    'ameliorating_actions': _("An action taken or circumstances altered to make better or compensate any harm after an incident."),
    'safety_barriers_failed': _("A safety barrier is a physical or non-physical means planned to prevent, control, or mitigate undesired events or accidents."),
    'safety_barriers_prevented': _("A safety barrier is a physical or non-physical means planned to prevent, control, or mitigate undesired events or accidents."),
    'actions_reduce_risk': _("Prevention activities planned or implemented within the radiation treatment centre and recommendations to minimize future harm."),
}

class SearchForm(forms.Form):
    """Form class used to allow users to input search parameters in order to generate a resutlant
    list of incidents.
    """

    incident_id = forms.IntegerField(label="Enter a unique incident ID")

    keyword = forms.CharField(label="Enter the keyword to search for")

    def __init__(self, *args, **kwargs):
        """Form initialization.
        """
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields['incident_id'].required = False
        self.fields['keyword'].required = False

class StatisticsForm(forms.Form):
    """Form class used to input desired parameters and filters for generating plots.
    """

    # Dynamically establish the available choices for years based on the current year
    YEAR_CHOICES = []
    YEAR_CHOICES.append(('','---------')) # empty option
    for r in range(2015, (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append((r,r))

    # Store all potential choices for all FK based models (with respect to Incident model)
    SINGLE_FILTER_CHOICES = []
    SINGLE_FILTER_CHOICES.append(('','---------')) # empty option
    SINGLE_FILTER_CHOICES.append(('All','All')) # empty option
    for field in models.Incident._meta.fields:
        if field.get_internal_type() == "ForeignKey" or field.get_internal_type() == "TreeForeignKey":
            cur_model = field.rel.to
            if cur_model != ILSUser and cur_model != models.Incident:
                choices = cur_model.objects.all()
                for choice in choices:
                    SINGLE_FILTER_CHOICES.append((choice.name, choice.name))
    for field in models.Incident._meta.many_to_many:
        cur_model = field.rel.to
        choices = cur_model.objects.all()
        for choice in choices:
            SINGLE_FILTER_CHOICES.append((choice.name, choice.name))
    SINGLE_FILTER_CHOICES = list(set(SINGLE_FILTER_CHOICES))

    # Store all potential ILSUsers
    SINGLE_USER_CHOICES = []
    SINGLE_USER_CHOICES.append(('','---------')) # empty option
    SINGLE_USER_CHOICES.append(('All','All')) # empty option
    for field in models.Incident._meta.fields:
        if field.get_internal_type() == "ForeignKey":
            cur_model = field.rel.to
            if cur_model == ILSUser:
                choices = cur_model.objects.all()
                for choice in choices:
                    # choice_key = choice.first_name + choice.last_name
                    # SINGLE_USER_CHOICES.append((choice_key, choice.get_name()))
                    # SINGLE_USER_CHOICES.append((choice.id, choice.id))
                    SINGLE_USER_CHOICES.append((choice.id, choice.get_name()))
    SINGLE_USER_CHOICES = list(set(SINGLE_USER_CHOICES))

    #fields:
    plot_type = forms.ModelChoiceField(label="Type of plot", queryset=models.StatPlotType.objects.all())

    parameter_type = forms.ModelChoiceField(label="Type of parameter", queryset=models.StatParameterType.objects.all())

    user_type = forms.ModelChoiceField(label="Parameter to Plot Events By", queryset=models.StatUserChoice.objects.all())

    user_single_choice = forms.ChoiceField(label="Choice to Filter Events By", choices=SINGLE_USER_CHOICES)

    fk_model_type = forms.ModelChoiceField(label="Parameter to Plot Events By", queryset=models.StatFKModelChoice.objects.all())

    fk_single_choice = forms.ChoiceField(label="Choice to Filter Events By", choices=SINGLE_FILTER_CHOICES)

    completion_filter = forms.ModelChoiceField(label="Filter Completion Status", queryset=models.StatCompletionFilter.objects.all())

    date_type = forms.ModelChoiceField(label="Date Type to Bin Events By", queryset=models.StatDateType.objects.all())

    date_bin = forms.ModelChoiceField(label="Date Binning", queryset=models.StatDateBin.objects.all())

    start_month = forms.ModelChoiceField(label="Start Month", queryset=models.Month.objects.all())

    start_year = forms.ChoiceField(label="Start Year", choices=YEAR_CHOICES)

    end_month = forms.ModelChoiceField(label="End Month", queryset=models.Month.objects.all())

    end_year = forms.ChoiceField(label="End Year", choices=YEAR_CHOICES)


    def __init__(self, *args, **kwargs):
        """Form initialization.
        """
        super(StatisticsForm, self).__init__(*args, **kwargs)

        self.fields['user_type'].required = False
        self.fields['user_single_choice'].required = False
        self.fields['fk_model_type'].required = False
        self.fields['fk_single_choice'].required = False
        self.fields['start_month'].required = False
        self.fields['end_month'].required = False
        self.fields['start_year'].required = False
        self.fields['end_year'].required = False

        # self.fields['fk_single_choice'].queryset = models.Month.objects.all()

    def clean(self):
        """Part of the form validation process, overriding to apply logic to form fields
        and generate errors if some field values are not appropriate.

        This method is involved with form validation. Three types of cleaning methods are 
        run during form processing; and are run when the is_valid() method is called on
        an instance of the form. The added features here are responsible for identifying
        errors in the inputted data, and applying them.
        """
        cleaned_data = super(StatisticsForm, self).clean()
        empty_year = ""

        # Generate errors if required fields based on type of parameter to be plotted, aren't filled
        parameter_type = cleaned_data.get('parameter_type')
        if parameter_type is None:
            self._errors['parameter_type'] = self.error_class(["This field is required."])
        else:
            if parameter_type.type_name == "key_field":
                if cleaned_data.get("fk_model_type") is None:
                    self._errors['fk_model_type'] = self.error_class(["This field is required."])
                if(cleaned_data.get("fk_single_choice") is None or cleaned_data.get("fk_single_choice") == ""):
                    self._errors['fk_single_choice'] = self.error_class(["This field is required."])
            elif parameter_type.type_name == "user_field":
                if cleaned_data.get("user_type") is None:
                    self._errors['user_type'] = self.error_class(["This field is required."])
                if(cleaned_data.get("user_single_choice") is None or cleaned_data.get("user_single_choice") == ""):
                    self._errors['user_single_choice'] = self.error_class(["This field is required."])

        # Make sure needed fields for date range are set if user should choose the range
        bin_object = cleaned_data.get('date_bin')
        if bin_object is None:
            self._errors['date_bin'] = self.error_class(["This field is required."])
        else:
            if bin_object.bin_name == "monthly_choose_range" and cleaned_data.get('start_year') == empty_year:
                self._errors['start_year'] = self.error_class(["Please select the year to begin the query"])
            if bin_object.bin_name == "monthly_choose_range" and cleaned_data.get('end_year') == empty_year:
                self._errors['end_year'] = self.error_class(["Please select the year to end the query"])
            if bin_object.bin_name == "monthly_choose_range" and cleaned_data.get('start_month') is None:
                self._errors['start_month'] = self.error_class(["Please select the month to begin the query"])
            if bin_object.bin_name == "monthly_choose_range" and cleaned_data.get('end_month') is None:
                self._errors['end_month'] = self.error_class(["Please select the month to end the query"])
            if "yearly" in bin_object.name.lower() and cleaned_data.get('start_year') == empty_year:
                self._errors['start_year'] = self.error_class(["Please select the year to begin the query"])
            if "yearly" in bin_object.name.lower() and cleaned_data.get('end_year') == empty_year:
                self._errors['end_year'] = self.error_class(["Please select the year to end the query"])

        return cleaned_data

class ChangeEventTypeForm(forms.ModelForm):
    """Form class used to change an incident's event type following initial report.
    """
    class Meta:
        """Define form fields
        """
        model = models.Incident
        
        fields = (
            'event_type',
            'number_patients_involved',
            'patient_id',
            'oncologist',
            'diagnosis',
            # 'treatment_site',
            'body_region_treated'
        )

    def __init__(self, *args, **kwargs):
        """Form initialization, specify required fields.
        """
        super(ChangeEventTypeForm, self).__init__(*args, **kwargs)

        self.fields['event_type'].required = True

        self.fields['oncologist'].queryset = ILSUser.objects.filter(is_oncologist=True)


    def clean(self):
        """Part of the form validation process, overriding to apply logic to form fields
        and generate errors if some field values are not appropriate.

        This method is involved with form validation. Three types of cleaning methods are 
        run during form processing; and are run when the is_valid() method is called on
        an instance of the form. The added features here are responsible for identifying
        errors in the inputted ata, and applying them.
        """
        cleaned_data = super(ChangeEventTypeForm, self).clean()

        # Error checking: read error response for meaning behind each
        # Handle issues with the event type / number of patients involved and the additional
        # fields for NMs and ACTs
        if cleaned_data.get("event_type") != None:
            if cleaned_data.get("event_type").pk == 3:
                if cleaned_data.get("number_patients_involved") == 0:
                    self._errors["number_patients_involved"] = self.error_class(["Actual incidents must have involved 1 or more patients. If no patients were involved, Event Type is "+models.EventType.objects.get(pk=1).name])
                elif cleaned_data.get("number_patients_involved") == 1:
                    if not cleaned_data.get("patient_id", "").strip():
                        self._errors["patient_id"] = self.error_class(["Actual incidents involving a single patient must include the patient ID"])
                    if cleaned_data.get("diagnosis") is None:
                        self._errors["diagnosis"] = self.error_class(["Actual incidents involving a single patient must include the patient's diagnosis"])
                    if cleaned_data.get("oncologist") is None:
                        self._errors["oncologist"] = self.error_class(["Actual incidents involving a single patient must indicate the primary physician associated with the treatment"])
                    # if not cleaned_data.get("treatment_site", "").strip():
                    #     self._errors["treatment_site"] = self.error_class(["Actual incidents involving a single patient must indicate the treatment site"])
                    if len(cleaned_data.get("body_region_treated")) == 0:
                        self._errors["body_region_treated"] = self.error_class(["Actual incidents involving a single patient must indicate the treatment site(s)"])
                elif cleaned_data.get("number_patients_involved") is None:
                    self._errors["number_patients_involved"] = self.error_class(["This field is required."])
            elif cleaned_data.get("event_type").pk == 2:
                if cleaned_data.get("number_patients_involved") == 0:
                    self._errors["number_patients_involved"] = self.error_class(["Near misses must have involved 1 or more patients. If no patients were involved, Event Type is "+models.EventType.objects.get(pk=1).name])
                elif cleaned_data.get("number_patients_involved") == 1:
                    if not cleaned_data.get("patient_id", "").strip():
                        self._errors["patient_id"] = self.error_class(["Near misses involving a single patient must include the patient ID"])
                    if cleaned_data.get("diagnosis") is None:
                        self._errors["diagnosis"] = self.error_class(["Near misses involving a single patient must include the patient's diagnosis"])
                    if cleaned_data.get("oncologist") is None:
                        self._errors["oncologist"] = self.error_class(["Near misses involving a single patient must indicate the primary physician associated with the treatment"])
                    # if not cleaned_data.get("treatment_site", "").strip():
                    #     self._errors["treatment_site"] = self.error_class(["Near misses involving a single patient must indicate the treatment site"])
                    if len(cleaned_data.get("body_region_treated")) == 0:
                        self._errors["body_region_treated"] = self.error_class(["Actual incidents involving a single patient must indicate the treatment site(s)"])
                elif cleaned_data.get("number_patients_involved") is None:
                    self._errors["number_patients_involved"] = self.error_class(["This field is required."])

        return cleaned_data

class IncidentReportForm(forms.ModelForm):
    """Form class used to input initial reported information for a radiotherapy incident.
    """
    # These fields are not defined within the model tied to this form (i.e. the Incident
    # model) and thus, must be defined explicitly
    auth_password = forms.CharField(label="Password", required=True)
    submitted_by = forms.CharField(label="Username", required=True)

    local_fields = ['id_coordinator_comments','id_support_required','id_support_given','id_support_description','id_investigator', 'id_submitted_by', 'id_auth_password']


    class Meta:
        """Define form fields, explicitly assign widgets to particular fields.
        """
        model = models.Incident

        # These are the fields which actually appear on the initial Report webpage. Some
        # of the additional fields included in the Incident model are not filled in until
        # the Investigation stage.
        fields = ('report_type','incident_id','event_type','number_patients_involved',
            'patient_id','oncologist','diagnosis',
            #'treatment_site',
            'body_region_treated','functional_work_area',
            'date_incident_detected','time_period_detected','incident_description',
            'descriptor','reported_by','reported_to',
            'patient_support_required','patient_support_given','patient_support_description',
            'support_required','support_given','support_description',
            'investigator','coordinator_comments','submitted_by','auth_password'
        )

        # Define explicit widgets for some fields
        widgets = {
            "incident_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "descriptor": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "patient_support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "coordinator_comments": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "auth_password": forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        """Form initialization: set required fields, placeholders, etc.
        """
        self.user = kwargs.pop("user")

        super(IncidentReportForm, self).__init__(*args, **kwargs)
        self.fields["date_incident_detected"].input_formats = ['%Y-%m-%d']

        # Put help_text as placeholder values in relevant fields (e.g. Patient id and Description)
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.help_text = field.help_text.replace(REMOVE_HELP_MESSAGE, "")
            if field:
                if field_name == "patient_id":
                    field.widget.attrs["placeholder"] = "Patient ID Number"
                elif field_name == "reported_by" or field_name == "reported_to":
                    field.widget.attrs["placeholder"] = "First Last"
                elif field_name == "number_patients_involved":
                    pass
                else:
                    field.widget.attrs["placeholder"] = field.help_text

        # #Don't need next four lines anymore (handled in the view)
        # try:
        #     initial_report_type = kwargs.pop("initial")['report_type'].name
        # except KeyError:
        #     initial_report_type = None

        self.fields['report_type'].required = True
        # self.fields['incident_id'].required = True
        self.fields['event_type'].required = True
        self.fields['functional_work_area'].required = True
        self.fields['date_incident_detected'].required = True
        self.fields['time_period_detected'].required = True
        self.fields['incident_description'].required = True
        # self.fields['number_patients_affected'].required = True
        # self.fields['number_patients_involved'].required = True
        self.fields['reported_by'].required = True
        self.fields['descriptor'].required = True
        self.fields['support_required'].required = True
        # self.fields['patient_support_required'].required = True
        self.fields['investigator'].required = True

        self.fields['coordinator_comments'].required = False

        self.fields['investigator'].queryset = ILSUser.objects.filter(is_investigator=True)
        self.fields['oncologist'].queryset = ILSUser.objects.filter(is_oncologist=True)

    def clean(self):
        """Part of the form validation process, overriding to apply logic to form fields
        and generate errors if some field values are not appropriate.

        This method is involved with form validation. Three types of cleaning methods are 
        run during form processing; and are run when the is_valid() method is called on
        an instance of the form. The added features here are responsible for identifying
        errors in the inputted ata, and applying them.
        """
        cleaned_data = super(IncidentReportForm, self).clean()
        # authenticate() returns a User object if valid, and None if invalid
        submitted_by = cleaned_data.get("submitted_by")
        password = cleaned_data.get("auth_password")
        self.user = authenticate(username=submitted_by, password=password)

        # Check username & password
        if self.user is not None:
            cleaned_data["submitted_by"] = self.user
        else:
            for n in ["submitted_by", "auth_password"]:
                if n in cleaned_data:
                    del cleaned_data[n]
                self._errors[n] = self.error_class(["Invalid Username & Password"])
        # Error checking: read error response for meaning behind each
        if cleaned_data.get("report_type").pk == 1 and not cleaned_data.get("reported_to", "").strip():
            self._errors["reported_to"] = self.error_class(["Incidents reported via a paper form must indicate who the paper report was submitted to"])
        if cleaned_data.get("report_type").pk == 1 and cleaned_data.get("incident_id") is None:
            self._errors["incident_id"] = self.error_class(["Incidents reported via a paper form must include the incident ID"])

        # Handle issues with the event type / number of patients involved and the additional
        # fields for NMs and ACTs
        if cleaned_data.get("event_type") != None:
            if cleaned_data.get("event_type").pk == 3:
                if cleaned_data.get("number_patients_involved") == 0:
                    self._errors["number_patients_involved"] = self.error_class(["Actual incidents must have involved 1 or more patients. If no patients were involved, Event Type is "+models.EventType.objects.get(pk=1).name])
                elif cleaned_data.get("number_patients_involved") == 1:
                    if not cleaned_data.get("patient_id", "").strip():
                        self._errors["patient_id"] = self.error_class(["Actual incidents involving a single patient must include the patient ID"])
                    if cleaned_data.get("diagnosis") is None:
                        self._errors["diagnosis"] = self.error_class(["Actual incidents involving a single patient must include the patient's diagnosis"])
                    if cleaned_data.get("oncologist") is None:
                        self._errors["oncologist"] = self.error_class(["Actual incidents involving a single patient must indicate the primary physician associated with the treatment"])
                    # if not cleaned_data.get("treatment_site", "").strip():
                    #     self._errors["treatment_site"] = self.error_class(["Actual incidents involving a single patient must indicate the treatment site"])
                    if len(cleaned_data.get("body_region_treated")) == 0:
                        self._errors["body_region_treated"] = self.error_class(["Actual incidents involving a single patient must indicate the treatment site(s)"])
                elif cleaned_data.get("number_patients_involved") is None:
                    self._errors["number_patients_involved"] = self.error_class(["This field is required."])
            elif cleaned_data.get("event_type").pk == 2:
                if cleaned_data.get("number_patients_involved") == 0:
                    self._errors["number_patients_involved"] = self.error_class(["Near misses must have involved 1 or more patients. If no patients were involved, Event Type is "+models.EventType.objects.get(pk=1).name])
                elif cleaned_data.get("number_patients_involved") == 1:
                    if not cleaned_data.get("patient_id", "").strip():
                        self._errors["patient_id"] = self.error_class(["Near misses involving a single patient must include the patient ID"])
                    if cleaned_data.get("diagnosis") is None:
                        self._errors["diagnosis"] = self.error_class(["Near misses involving a single patient must include the patient's diagnosis"])
                    if cleaned_data.get("oncologist") is None:
                        self._errors["oncologist"] = self.error_class(["Near misses involving a single patient must indicate the primary physician associated with the treatment"])
                    # if not cleaned_data.get("treatment_site", "").strip():
                    #     self._errors["treatment_site"] = self.error_class(["Near misses involving a single patient must indicate the treatment site"])
                    if len(cleaned_data.get("body_region_treated")) == 0:
                        self._errors["body_region_treated"] = self.error_class(["Near misses involving a single patient must indicate the treatment site(s)"])
                elif cleaned_data.get("number_patients_involved") is None:
                    self._errors["number_patients_involved"] = self.error_class(["This field is required."])
            # elif cleaned_data.get("event_type").pk == 0:
            #     if cleaned_data.get("number_patients_involved") != 0:
            #         self._errors["number_patients_involved"] = self.error_class(["Reportable circumstances do not involve any patients."])

        if cleaned_data.get("event_type") != None:
            if cleaned_data.get("event_type").pk == 2 or cleaned_data.get("event_type").pk == 3:
                if cleaned_data.get("patient_support_required") == None:
                    self._errors["patient_support_required"] = self.error_class(["This field is required."])

        # Handle support related field errors
        if cleaned_data.get("support_required") != None:
            if cleaned_data.get("support_required").pk == 1 and cleaned_data.get("support_given") is None:
                self._errors["support_given"] = self.error_class(["Please indicate whether the needed support has been offered to staff"])
            if cleaned_data.get("support_required").pk == 1 and not cleaned_data.get("support_description", "").strip():
                self._errors["support_description"] = self.error_class(["Please describe the support required by staff"])

        if cleaned_data.get("patient_support_required") != None:
            if cleaned_data.get("patient_support_required").pk == 1 and cleaned_data.get("patient_support_given") is None:
                self._errors["patient_support_given"] = self.error_class(["Please indicate whether the needed support has been offered to the patient(s)"])
            if cleaned_data.get("patient_support_required").pk == 1 and not cleaned_data.get("patient_support_description", "").strip():
                self._errors["patient_support_description"] = self.error_class(["Please describe the support required by the patient(s)"])

        return cleaned_data


#-----------------------------------------------------------------------------------------
# The following two Widget classes are required for creating selection fields that have
# have some disabled fields. This is necessary for the tree-structured fields within the
# NSIR-RT taxonomy that do not allow selection of parent choices. The first class is used
# for single select fields, and the second is used for multi-select fields.
#-----------------------------------------------------------------------------------------
class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<select{0}>', flatatt(final_attrs))]
        output.append(u'<option value="" selected="selected">---------</option>\n')
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))

class SelectMultipleWithDisabled(SelectMultiple):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))


class IncidentImageForm(forms.ModelForm):
    """Form class used to save a new incident image.
    """
    class Meta:
        """Define form fields and widgets.
        """
        model = models.IncidentImage

        fields = ('image', 'image_name', 'incident')

    def __init__(self, *args, **kwargs):
        """Set required fields and widget attributes.
        """
        super(IncidentImageForm, self).__init__(*args, **kwargs)

        # Readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        self.fields['image'].required = True
        self.fields['image_name'].required = True
        # self.fields['incident'].widget = HiddenInput()

    def clean(self):
        """Apply errors.
        """
        cleaned_data = super(IncidentImageForm, self).clean()
        # Error checking: read error response for meaning behind each
        image = self.cleaned_data.get('image',False)
        if not image:
            self._errors["image"] = self.error_class(["No image file selected."])
        elif image._size > settings.MAX_IMAGE_SIZE*1024*1024:
            self._errors["image"] = self.error_class(["File is too large (Max size: "+str(settings.MAX_IMAGE_SIZE)+"MB)"])

        return cleaned_data

class TemplateForm(forms.ModelForm):
    """Form class used to save field inputs as a template for a predefined incident type
    """
    class Meta:
        """Define form fields and widgets.
        """
        model = models.PredefinedIncident

        fields = ('name', 'description')

        widgets = {
            "description": forms.Textarea(attrs={"class": "input-block-level", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """Set required fields and widget attributes.
        """
        super(TemplateForm, self).__init__(*args, **kwargs)

        # Readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        self.fields['name'].required = True
        self.fields['description'].required = True

        self.fields['description'].widget.attrs["placeholder"] = self.fields['description'].help_text



class InvalidForm(forms.ModelForm):
    """Form class used to mark an incident as invalid for trending.
    """
    class Meta:
        model = models.Incident
        fields = ('invalid_reason',)

        widgets = {
            "invalid_reason": forms.Textarea(attrs={"class": "input-block-level", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """Set required fields.
        """
        super(InvalidForm, self).__init__(*args, **kwargs)

        # Readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        self.fields['invalid_reason'].required = True

    def clean(self):
        """Apply errors.
        """
        cleaned_data = super(InvalidForm, self).clean()
        # Error checking: read error response for meaning behind each
        if not cleaned_data.get("invalid_reason", "").strip():
            self._errors["invalid_reason"] = self.error_class(["Please indicate why you are labeling this incident as invalid for trending"])

        return cleaned_data



class ValidForm(forms.ModelForm):
    """Form class used to re-open the investigation for an incident which was previously
    flagged as invalid for trending.
    """
    class Meta:
        model = models.Incident
        fields = ('valid',)

    def __init__(self, *args, **kwargs):
        """Explicitly include init.
        """
        super(ValidForm, self).__init__(*args, **kwargs)



class InvestigationForm(forms.ModelForm):
    """Form class used to input investigation information for actual incidents.

    This form should not be used for reportable circumstances or near-misses. Different
    fields are provided on the investigatio page depending on the incident type, hence
    the need for different form classes.
    """

    # Assign fields with id_ prefix to arrays, so they may be presented distinctly in the
    # template. HTML form fields generated via a Django form are automatically created
    # with the id_ prefix, hence its inclusion here.
    local_fields = ['id_report_type','id_reported_by','id_reported_to','id_submitted_by','id_submitted','id_patient_id','id_oncologist','id_descriptor']
    investigator_fields = ['id_investigator', 'id_flag', 'id_discussion', 'id_hospital_form_id', 'id_predefined_type']
    support_fields = ['id_patient_support_required', 'id_patient_support_given', 'id_patient_support_description', 'id_support_required', 'id_support_given', 'id_support_description']
    impact_fields = ['id_incident_description', 'id_coordinator_comments', 'id_event_type', 'id_local_severity_level', 'id_dosimetric_impact', 'id_latent_medical_harm']
    discovery_fields = ['id_functional_work_area', 'id_date_incident_detected', 'id_date_incident_occurred', 'id_time_period_detected', 'id_time_period_occurred', 'id_individual_detected', 'id_individual_involved']
    patient_fields = ['id_patient_month_birth', 'id_patient_year_birth', 'id_patient_gender', 'id_diagnosis']
    details_fields = ['id_process_step_occurred', 'id_process_step_detected', 'id_problem_type', 'id_secondary_problem_type', 'id_contributing_factors', 'id_number_patients_involved']
    treatment_delivery_fields = ['id_radiation_treatment_techniques', 'id_total_dose_prescribed', 'id_number_fractions_prescribed', 'id_number_fractions_incorrect', 'id_hardware_manufacturer_model', 'id_software_manufacturer_model', 'id_body_region_treated', 'id_treatment_intent']
    investigation_fields = ['id_investigation_narrative', 'id_patient_disclosure', 'id_ameliorating_actions', 'id_safety_barriers_failed', 'id_safety_barriers_prevented', 'id_actions_reduce_risk']

    class Meta:
        """Define form fields, explicitly assign widgets to particular fields.
        """
        model = models.Incident

        fields = (
            #local
            'report_type',
            'reported_by',
            'reported_to',
            'submitted_by',
            'submitted',
            'patient_id',
            'oncologist',
            # 'treatment_site',
            'descriptor',
            #investigator
            'investigator',
            'flag',
            'discussion',
            'hospital_form_id',
            'predefined_type',
            #support
            'patient_support_required',
            'patient_support_given',
            'patient_support_description',
            'support_required',
            'support_given',
            'support_description',
            #impact
            'incident_description',
            'coordinator_comments',
            'event_type',
            # 'acute_medical_harm',
            'local_severity_level',
            'dosimetric_impact',
            'latent_medical_harm',
            #discovery
            'functional_work_area',
            'date_incident_detected',
            'date_incident_occurred',
            'time_period_detected',
            'time_period_occurred',
            'individual_detected',
            'individual_involved',
            #patient
            'patient_month_birth',
            'patient_year_birth',
            'patient_gender',
            'diagnosis',
            #details
            'process_step_occurred',
            'process_step_detected',
            'problem_type',
            'secondary_problem_type',
            'contributing_factors',
            'number_patients_involved',
            #treatment delivery
            'radiation_treatment_techniques',
            'total_dose_prescribed',
            'number_fractions_prescribed',
            'number_fractions_incorrect',
            'hardware_manufacturer_model',
            'software_manufacturer_model',
            'body_region_treated',
            'treatment_intent',
            #investigation
            'investigation_narrative',
            'patient_disclosure',
            'ameliorating_actions',
            'safety_barriers_failed',
            'safety_barriers_prevented',
            'actions_reduce_risk',
        )

        # Mutiple select widgets use custom widgets to prevent parent nodes within the
        # tree structure from being selected (see NSIR-RT taxonomy). In other words, only
        # child nodes should be allowed to be selected. Assignment of attrs to these
        # custom widgets also includes specifying a HTML classes to ensure the select
        # boxes are long enought to accomodate all options and wide enough to accomodate 
        # full text of the longer choices.
        widgets = {
            "descriptor": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "patient_support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "incident_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            "coordinator_comments": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            #"individual_detected": FilteredSelectMultiple("", is_stacked=False),
            "individual_detected": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "individual_involved": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "problem_type": SelectWithDisabled(),
            "secondary_problem_type": SelectMultipleWithDisabled(attrs={'size':str(models.SecondaryProblemType.objects.count()),'class': 'multi_select_width'}),
            "contributing_factors": SelectMultipleWithDisabled(attrs={'size':str(models.ContributingFactor.objects.count()),'class': 'multi_select_width'}),
            "radiation_treatment_techniques": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "ameliorating_actions": SelectMultipleWithDisabled(attrs={'size':str(models.AmelioratingAction.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_failed": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierFailed.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_prevented": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierPrevented.objects.count()),'class': 'multi_select_width'}),
            "actions_reduce_risk": SelectMultipleWithDisabled(attrs={'size':str(models.ActionReduceRisk.objects.count()),'class': 'multi_select_width'}),
            "hardware_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "software_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),    
            #"body_region_treated": forms.SelectMultiple(attrs={'size':str(models.BodyRegionTreated.objects.count())}),
            "investigation_narrative": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
        }

    def get_choices(self,queryset):
        """Supply the available choices for tree structured form fields.

        Returns:
            An array of choices. Each element of the array is a tuple containing the level
            of that option (each is just incremented by 1), as well as the unicode value
            for the label (including the correct number of '---' prefixes depending on 
            how many parent options that option has). If the option is a parent option, 
            that option is disabled (cannot be selected).
        """
        mptt_opts = queryset.model._mptt_meta
        queryset = queryset.order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)
        level_indicator = u'---'

        choices = []
        for item in queryset:
            level = getattr(item, item._mptt_meta.level_attr)
            value = item.id
            label = mark_safe(conditional_escape(level_indicator) * level + smart_unicode(item.name))
            if item.is_leaf_node():
                choices.append((value, label))
            else:
                choices.append((value, {'label': label, 'disabled': True}))
        return choices

    def __init__(self, *args, **kwargs):
        """Form initialization: set immutable (readonly) fields so that initially reported
        fields cannot be changed, required fields, etc.
        """
        if 'user' in kwargs:
            user = kwargs['user']
            del kwargs['user']
        else:
            user = None

        if 'investigator_key' in kwargs:
            investigator_key = kwargs['investigator_key']
            del kwargs['investigator_key']
        else:
            investigator_key = None

        super(InvestigationForm, self).__init__(*args, **kwargs)

        # Remove the default help message for multi select fields
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.help_text = field.help_text.replace(REMOVE_HELP_MESSAGE, "")

        # Assign html class indicating whether or not the field can be edited or not by
        # the current user
        reported_fields = self.instance.get_reported_field_ids()
        if not user.can_edit(investigator_pk=investigator_key):
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        self.fields[field].widget.attrs['readonly'] = True
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " blocked-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "blocked-field"
        else:
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " editable-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "editable-field"                   

        # Assign class to readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        for field in reported_fields:
            try:
                self.fields[field].widget.attrs['readonly'] = True
                existing_class = self.fields[field].widget.attrs['class']
                existing_class = existing_class + " reported-field"
                self.fields[field].widget.attrs['class'] = existing_class
            except KeyError:
                self.fields[field].widget.attrs['class'] = "reported-field"

        self.fields['investigation_narrative'].widget.attrs["placeholder"] = self.fields['investigation_narrative'].help_text

        # Need to set tree structure fields as not required
        self.fields['problem_type'].required = False
        self.fields['secondary_problem_type'].required = False
        self.fields['contributing_factors'].required = False
        self.fields['ameliorating_actions'].required = False
        self.fields['safety_barriers_prevented'].required = False
        self.fields['safety_barriers_failed'].required = False
        self.fields['actions_reduce_risk'].required = False

        # Make multi-select wiget long enough for non-tree structured multi selects
        self.fields['individual_detected'].widget.attrs['size'] = str(models.IndividualDetected.objects.count())
        self.fields['individual_involved'].widget.attrs['size'] = str(models.IndividualInvolved.objects.count())
        self.fields['body_region_treated'].widget.attrs['size'] = str(models.BodyRegionTreated.objects.count())
        self.fields['secondary_problem_type'].widget.attrs['size'] = str(models.SecondaryProblemType.objects.count())
        self.fields['radiation_treatment_techniques'].widget.attrs['size'] = str(models.RadiationTreatmentTechnique.objects.count())

        # Do not allow there to be no investigator assigned to an investigation
        self.fields['investigator'].empty_label = None
        self.fields['investigator'].queryset = ILSUser.objects.filter(is_investigator=True)
        self.fields['local_severity_level'].queryset = models.LocalSeverityLevel.objects.filter(pk__gte=3)

        self.fields["date_incident_detected"].input_formats = ['%Y-%m-%d']

        # Indicate levels in the tree structure (below each parent, add ---)
        self.level_indicator = kwargs.pop('level_indicator', u'---')

        # Need to explicitly assign choices to tree structure fields
        self.fields['problem_type'].choices = self.get_choices(queryset=models.ProblemType.objects.all())
        self.fields['secondary_problem_type'].choices = self.get_choices(queryset=models.SecondaryProblemType.objects.all())
        self.fields['contributing_factors'].choices = self.get_choices(queryset=models.ContributingFactor.objects.all())
        self.fields['ameliorating_actions'].choices = self.get_choices(queryset=models.AmelioratingAction.objects.all())
        self.fields['safety_barriers_failed'].choices = self.get_choices(queryset=models.SafetyBarrierFailed.objects.all())
        self.fields['safety_barriers_prevented'].choices = self.get_choices(queryset=models.SafetyBarrierPrevented.objects.all())
        self.fields['actions_reduce_risk'].choices = self.get_choices(queryset=models.ActionReduceRisk.objects.all())

    def save(self, *args, **kwargs):
        """Update the investigation (does not require all fields to be filled).
        """
        super(InvestigationForm, self).save(*args, **kwargs)

        if "commit" not in kwargs or kwargs["commit"]:
            self.instance.incident.save()

        return self.instance



class InvestigationRCForm(forms.ModelForm):
    """Form class used to input investigation information for reportable circumstances.

    This form should not be used for near-misses, or actual incidents. For additional
    comments, please see the InvestigationForm for actual incidents provided above. 
    """

    local_fields = ['id_report_type','id_reported_by','id_reported_to','id_submitted_by','id_submitted','id_descriptor']
    investigator_fields = ['id_investigator', 'id_flag', 'id_discussion', 'id_hospital_form_id', 'id_predefined_type']
    support_fields = ['id_patient_support_required', 'id_patient_support_given', 'id_patient_support_description', 'id_support_required', 'id_support_given', 'id_support_description']
    impact_fields = ['id_incident_description', 'id_coordinator_comments', 'id_event_type']
    discovery_fields = ['id_functional_work_area', 'id_date_incident_detected', 'id_date_incident_occurred', 'id_time_period_detected', 'id_time_period_occurred', 'id_individual_detected', 'id_individual_involved']
    patient_fields = []
    details_fields = ['id_process_step_occurred', 'id_process_step_detected', 'id_problem_type', 'id_secondary_problem_type', 'id_contributing_factors', 'id_number_patients_involved']
    treatment_delivery_fields = ['id_radiation_treatment_techniques', 'id_hardware_manufacturer_model', 'id_software_manufacturer_model']
    investigation_fields = ['id_investigation_narrative', 'id_ameliorating_actions', 'id_safety_barriers_failed', 'id_safety_barriers_prevented', 'id_actions_reduce_risk']

    class Meta:
        model = models.Incident

        fields = (
            #local
            'report_type',
            'reported_by',
            'reported_to',
            'submitted_by',
            'submitted',
            'descriptor',
            #investigator
            'investigator',
            'flag',
            'discussion',
            'hospital_form_id',
            'predefined_type',
            #support
            'patient_support_required',
            'patient_support_given',
            'patient_support_description',
            'support_required',
            'support_given',
            'support_description',
            #impact
            'incident_description',
            'coordinator_comments',
            'event_type',
            #discovery
            'functional_work_area',
            'date_incident_detected',
            'date_incident_occurred',
            'time_period_detected',
            'time_period_occurred',
            'individual_detected',
            'individual_involved',
            #patient
            #details
            'process_step_occurred',
            'process_step_detected',
            'problem_type',
            'secondary_problem_type',
            'contributing_factors',
            'number_patients_involved',
            #treatment delivery
            'radiation_treatment_techniques',
            'hardware_manufacturer_model',
            'software_manufacturer_model',
            #investigation
            'investigation_narrative',
            'ameliorating_actions',
            'safety_barriers_failed',
            'safety_barriers_prevented',
            'actions_reduce_risk',
        )

        widgets = {
            "descriptor": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "patient_support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "incident_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            "coordinator_comments": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            #"individual_detected": FilteredSelectMultiple("", is_stacked=False),
            "individual_detected": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "individual_involved": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "problem_type": SelectWithDisabled(),
            "secondary_problem_type": SelectMultipleWithDisabled(attrs={'size':str(models.SecondaryProblemType.objects.count()),'class': 'multi_select_width'}),
            "contributing_factors": SelectMultipleWithDisabled(attrs={'size':str(models.ContributingFactor.objects.count()),'class': 'multi_select_width'}),
            "radiation_treatment_techniques": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "ameliorating_actions": SelectMultipleWithDisabled(attrs={'size':str(models.AmelioratingAction.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_failed": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierFailed.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_prevented": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierPrevented.objects.count()),'class': 'multi_select_width'}),
            "actions_reduce_risk": SelectMultipleWithDisabled(attrs={'size':str(models.ActionReduceRisk.objects.count()),'class': 'multi_select_width'}),

            "hardware_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "software_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),    
            #"body_region_treated": forms.SelectMultiple(attrs={'size':str(models.BodyRegionTreated.objects.count())}),
            "investigation_narrative": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
        }

    def get_choices(self,queryset):
        mptt_opts = queryset.model._mptt_meta
        queryset = queryset.order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)
        level_indicator = u'---'

        choices = []
        for item in queryset:
            level = getattr(item, item._mptt_meta.level_attr)
            value = item.id
            label = mark_safe(conditional_escape(level_indicator) * level + smart_unicode(item.name))
            if item.is_leaf_node():
                choices.append((value, label))
            else:
                choices.append((value, {'label': label, 'disabled': True}))
        return choices

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs['user']
            del kwargs['user']
        else:
            user = None

        if 'investigator_key' in kwargs:
            investigator_key = kwargs['investigator_key']
            del kwargs['investigator_key']
        else:
            investigator_key = None

        super(InvestigationRCForm, self).__init__(*args, **kwargs)

        # Remove the default help message for multi select fields
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.help_text = field.help_text.replace(REMOVE_HELP_MESSAGE, "")

        # Assign html class indicating whether or not the field can be edited or not by
        # the current user
        reported_fields = self.instance.get_reported_field_ids()
        if not user.can_edit(investigator_pk=investigator_key):
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        self.fields[field].widget.attrs['readonly'] = True
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " blocked-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "blocked-field"
        else:
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " editable-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "editable-field"                   

        # Assign class to readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        for field in reported_fields:
            try:
                self.fields[field].widget.attrs['readonly'] = True
                existing_class = self.fields[field].widget.attrs['class']
                existing_class = existing_class + " reported-field"
                self.fields[field].widget.attrs['class'] = existing_class
            except KeyError:
                self.fields[field].widget.attrs['class'] = "reported-field"

        self.fields['investigation_narrative'].widget.attrs["placeholder"] = self.fields['investigation_narrative'].help_text

        # Additional settings
        self.fields['problem_type'].required = False
        self.fields['secondary_problem_type'].required = False
        self.fields['contributing_factors'].required = False
        self.fields['ameliorating_actions'].required = False
        self.fields['safety_barriers_prevented'].required = False
        self.fields['safety_barriers_failed'].required = False
        self.fields['actions_reduce_risk'].required = False

        self.fields['individual_detected'].widget.attrs['size'] = str(models.IndividualDetected.objects.count())
        self.fields['individual_involved'].widget.attrs['size'] = str(models.IndividualInvolved.objects.count())
        self.fields['radiation_treatment_techniques'].widget.attrs['size'] = str(models.RadiationTreatmentTechnique.objects.count())

        self.fields['investigator'].empty_label = None
        self.fields['investigator'].queryset = ILSUser.objects.filter(is_investigator=True)

        self.fields["date_incident_detected"].input_formats = ['%Y-%m-%d']

        self.fields['problem_type'].choices = self.get_choices(queryset=models.ProblemType.objects.all())
        self.fields['secondary_problem_type'].choices = self.get_choices(queryset=models.SecondaryProblemType.objects.all())
        self.fields['contributing_factors'].choices = self.get_choices(queryset=models.ContributingFactor.objects.all())
        self.fields['ameliorating_actions'].choices = self.get_choices(queryset=models.AmelioratingAction.objects.all())
        self.fields['safety_barriers_failed'].choices = self.get_choices(queryset=models.SafetyBarrierFailed.objects.all())
        self.fields['safety_barriers_prevented'].choices = self.get_choices(queryset=models.SafetyBarrierPrevented.objects.all())
        self.fields['actions_reduce_risk'].choices = self.get_choices(queryset=models.ActionReduceRisk.objects.all())

    def save(self, *args, **kwargs):
        super(InvestigationRCForm, self).save(*args, **kwargs)

        if "commit" not in kwargs or kwargs["commit"]:
            self.instance.incident.save()

        return self.instance



class InvestigationNMForm(forms.ModelForm):
    """Form class used to input investigation information for near-misses.

    This form should not be used for reportable circumstances, or actual incidents. For
    additional comments, please see the InvestigationForm for actual incidents provided
    above.
    """

    local_fields = ['id_report_type','id_reported_by','id_reported_to','id_submitted_by','id_submitted','id_patient_id','id_oncologist','id_descriptor']
    investigator_fields = ['id_investigator', 'id_flag', 'id_discussion', 'id_hospital_form_id', 'id_predefined_type']
    support_fields = ['id_patient_support_required', 'id_patient_support_given', 'id_patient_support_description', 'id_support_required', 'id_support_given', 'id_support_description']
    impact_fields = ['id_incident_description', 'id_coordinator_comments', 'id_event_type']
    discovery_fields = ['id_functional_work_area', 'id_date_incident_detected', 'id_date_incident_occurred', 'id_time_period_detected', 'id_time_period_occurred', 'id_individual_detected', 'id_individual_involved']
    patient_fields = ['id_patient_month_birth', 'id_patient_year_birth', 'id_patient_gender', 'id_diagnosis']
    details_fields = ['id_process_step_occurred', 'id_process_step_detected', 'id_problem_type', 'id_secondary_problem_type', 'id_contributing_factors', 'id_number_patients_involved']
    treatment_delivery_fields = ['id_radiation_treatment_techniques', 'id_total_dose_prescribed', 'id_number_fractions_prescribed', 'id_hardware_manufacturer_model', 'id_software_manufacturer_model', 'id_body_region_treated', 'id_treatment_intent']
    investigation_fields = ['id_investigation_narrative', 'id_ameliorating_actions', 'id_safety_barriers_failed', 'id_safety_barriers_prevented', 'id_actions_reduce_risk']

    class Meta:
        model = models.Incident

        fields = (
            #local
            'report_type',
            'reported_by',
            'reported_to',
            'submitted_by',
            'submitted',
            'patient_id',
            'oncologist',
            # 'treatment_site',
            'descriptor',
            #investigator
            'investigator',
            'flag',
            'discussion',
            'hospital_form_id',
            'predefined_type',
            #support
            'patient_support_required',
            'patient_support_given',
            'patient_support_description',
            'support_required',
            'support_given',
            'support_description',
            #impact
            'incident_description',
            'coordinator_comments',
            'event_type',
            #discovery
            'functional_work_area',
            'date_incident_detected',
            'date_incident_occurred',
            'time_period_detected',
            'time_period_occurred',
            'individual_detected',
            'individual_involved',
            #patient
            'patient_month_birth',
            'patient_year_birth',
            'patient_gender',
            'diagnosis',
            #details
            'process_step_occurred',
            'process_step_detected',
            'problem_type',
            'secondary_problem_type',
            'contributing_factors',
            'number_patients_involved',
            #treatment delivery
            'radiation_treatment_techniques',
            'total_dose_prescribed',
            'number_fractions_prescribed',
            'hardware_manufacturer_model',
            'software_manufacturer_model',
            'body_region_treated',
            'treatment_intent',
            #investigation
            'investigation_narrative',
            'ameliorating_actions',
            'safety_barriers_failed',
            'safety_barriers_prevented',
            'actions_reduce_risk',
        )

        widgets = {
            "descriptor": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "patient_support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "support_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "incident_description": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            "coordinator_comments": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),    
            #"individual_detected": FilteredSelectMultiple("", is_stacked=False),
            "individual_detected": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "individual_involved": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "problem_type": SelectWithDisabled(),
            "secondary_problem_type": SelectMultipleWithDisabled(attrs={'size':str(models.SecondaryProblemType.objects.count()),'class': 'multi_select_width'}),
            "contributing_factors": SelectMultipleWithDisabled(attrs={'size':str(models.ContributingFactor.objects.count()),'class': 'multi_select_width'}),
            "radiation_treatment_techniques": forms.SelectMultiple(attrs={'class': 'multi_select_width'}),
            "ameliorating_actions": SelectMultipleWithDisabled(attrs={'size':str(models.AmelioratingAction.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_failed": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierFailed.objects.count()),'class': 'multi_select_width'}),
            "safety_barriers_prevented": SelectMultipleWithDisabled(attrs={'size':str(models.SafetyBarrierPrevented.objects.count()),'class': 'multi_select_width'}),
            "actions_reduce_risk": SelectMultipleWithDisabled(attrs={'size':str(models.ActionReduceRisk.objects.count()),'class': 'multi_select_width'}),

            "hardware_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),
            "software_manufacturer_model": forms.Textarea(attrs={"class": "input-block-level", "rows": 2}),    
            #"body_region_treated": forms.SelectMultiple(attrs={'size':str(models.BodyRegionTreated.objects.count())}),
            "investigation_narrative": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
        }

    def get_choices(self,queryset):
        mptt_opts = queryset.model._mptt_meta
        queryset = queryset.order_by(mptt_opts.tree_id_attr, mptt_opts.left_attr)
        level_indicator = u'---'

        choices = []
        for item in queryset:
            level = getattr(item, item._mptt_meta.level_attr)
            value = item.id
            label = mark_safe(conditional_escape(level_indicator) * level + smart_unicode(item.name))
            if item.is_leaf_node():
                choices.append((value, label))
            else:
                choices.append((value, {'label': label, 'disabled': True}))
        return choices

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs['user']
            del kwargs['user']
        else:
            user = None

        if 'investigator_key' in kwargs:
            investigator_key = kwargs['investigator_key']
            del kwargs['investigator_key']
        else:
            investigator_key = None

        super(InvestigationNMForm, self).__init__(*args, **kwargs)

        # Remove the default help message for multi select fields
        for field_name in self.fields:
            field = self.fields.get(field_name)
            field.help_text = field.help_text.replace(REMOVE_HELP_MESSAGE, "")

        # Assign html class indicating whether or not the field can be edited or not by
        # the current user
        reported_fields = self.instance.get_reported_field_ids()
        if not user.can_edit(investigator_pk=investigator_key):
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        self.fields[field].widget.attrs['readonly'] = True
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " blocked-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "blocked-field"
        else:
            for field in self.fields:
                if field not in reported_fields and not field == "flag":
                    try:
                        existing_class = self.fields[field].widget.attrs['class']
                        existing_class = existing_class + " editable-field"
                        self.fields[field].widget.attrs['class'] = existing_class
                    except KeyError:
                        self.fields[field].widget.attrs['class'] = "editable-field"                   

        # Assign class to readonly fields which were saved in the initial report
        #self.fields[''].widget.attrs['readonly'] = True
        for field in reported_fields:
            try:
                self.fields[field].widget.attrs['readonly'] = True
                existing_class = self.fields[field].widget.attrs['class']
                existing_class = existing_class + " reported-field"
                self.fields[field].widget.attrs['class'] = existing_class
            except KeyError:
                self.fields[field].widget.attrs['class'] = "reported-field"

        self.fields['investigation_narrative'].widget.attrs["placeholder"] = self.fields['investigation_narrative'].help_text

        # Additional settings
        self.fields['problem_type'].required = False
        self.fields['secondary_problem_type'].required = False
        self.fields['contributing_factors'].required = False
        self.fields['ameliorating_actions'].required = False
        self.fields['safety_barriers_prevented'].required = False
        self.fields['safety_barriers_failed'].required = False
        self.fields['actions_reduce_risk'].required = False

        self.fields['individual_detected'].widget.attrs['size'] = str(models.IndividualDetected.objects.count())
        self.fields['individual_involved'].widget.attrs['size'] = str(models.IndividualInvolved.objects.count())
        self.fields['body_region_treated'].widget.attrs['size'] = str(models.BodyRegionTreated.objects.count())
        self.fields['radiation_treatment_techniques'].widget.attrs['size'] = str(models.RadiationTreatmentTechnique.objects.count())

        self.fields['investigator'].empty_label = None
        self.fields['investigator'].queryset = ILSUser.objects.filter(is_investigator=True)

        self.fields["date_incident_detected"].input_formats = ['%Y-%m-%d']

        self.fields['problem_type'].choices = self.get_choices(queryset=models.ProblemType.objects.all())
        self.fields['secondary_problem_type'].choices = self.get_choices(queryset=models.SecondaryProblemType.objects.all())
        self.fields['contributing_factors'].choices = self.get_choices(queryset=models.ContributingFactor.objects.all())
        self.fields['ameliorating_actions'].choices = self.get_choices(queryset=models.AmelioratingAction.objects.all())
        self.fields['safety_barriers_failed'].choices = self.get_choices(queryset=models.SafetyBarrierFailed.objects.all())
        self.fields['safety_barriers_prevented'].choices = self.get_choices(queryset=models.SafetyBarrierPrevented.objects.all())
        self.fields['actions_reduce_risk'].choices = self.get_choices(queryset=models.ActionReduceRisk.objects.all())

    def save(self, *args, **kwargs):
        super(InvestigationNMForm, self).save(*args, **kwargs)

        if "commit" not in kwargs or kwargs["commit"]:
            self.instance.incident.save()

        return self.instance


class ActionCreateForm(forms.ModelForm):
    """Form class used to create an IncidentAction object, tied to an Incident instance.
    """

    class Meta:
        """Define form fields, explicitly assign widgets to particular fields.
        """
        model = models.IncidentAction


        fields = ('description_proposed','responsible',
        )

        # Define explicit widgets for some fields
        widgets = {
            "description_proposed": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        """Form initialization: set required fields, placeholders, etc.
        """

        super(ActionCreateForm, self).__init__(*args, **kwargs)

        self.fields['description_proposed'].required = True
        self.fields['responsible'].required = True

        self.fields['responsible'].queryset = ILSUser.objects.filter(is_investigator=True)

    def clean(self):
        """Part of the form validation process, overriding to apply logic to form fields
        and generate errors if some field values are not appropriate.

        This method is involved with form validation. Three types of cleaning methods are 
        run during form processing; and are run when the is_valid() method is called on
        an instance of the form. The added features here are responsible for identifying
        errors in the inputted ata, and applying them.
        """
        cleaned_data = super(ActionCreateForm, self).clean()
        if not cleaned_data.get("description_proposed", "").strip():
            self._errors["description_proposed"] = self.error_class(["Please explain the action to be taken"])

        return cleaned_data

class ActionUpdateForm(forms.ModelForm):
    """Form class used to update an IncidentAction object, tied to an Incident instance.
    """

    # Needed to tie new IncidentActions created using ActionCreateForm to an ActionUpdateFORM
    # without having to reload the page. Field will store the pk associated with new
    # IncidentAction
    instance_id = forms.CharField(required=False)

    class Meta:
        """Define form fields, explicitly assign widgets to particular fields.
        """
        model = models.IncidentAction

        fields = (
            'description_proposed','responsible',
            'complete','description_performed',
            'instance_id',
        )

        # Define explicit widgets for some fields
        widgets = {
            "description_proposed": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "description_performed": forms.Textarea(attrs={"class": "input-block-level", "rows": 6}),
            "complete": forms.CheckboxInput(attrs={"class": "action-complete"}),
            "responsible": forms.Select(attrs={"class": "action-responsible reported-field"}),
        }

    def __init__(self, *args, **kwargs):
        """Form initialization: set readonly fields, querysets, etc.
        """

        super(ActionUpdateForm, self).__init__(*args, **kwargs)

        # self.fields['description_performed'].required = True
        # self.fields['complete'].required = True

        blockable_fields = ['complete','description_performed']

        self.fields['description_proposed'].widget.attrs['readonly'] = True
        self.fields['responsible'].widget.attrs['readonly'] = True

        instance = getattr(self, 'instance', None)
        if instance.complete:
            for field in blockable_fields:
                self.fields[field].widget.attrs['readonly'] = True
                try:
                    existing_class = self.fields[field].widget.attrs['class']
                    existing_class = existing_class + " blocked-action-field"
                    self.fields[field].widget.attrs['class'] = existing_class
                except KeyError:
                    self.fields[field].widget.attrs['class'] = "blocked-action-field"
        else:
            for field in blockable_fields:
                try:
                    existing_class = self.fields[field].widget.attrs['class']
                    existing_class = existing_class + " editable-action-field"
                    self.fields[field].widget.attrs['class'] = existing_class
                except KeyError:
                    self.fields[field].widget.attrs['class'] = "editable-action-field"

        self.fields['responsible'].queryset = ILSUser.objects.filter(is_investigator=True)

    def clean(self):
        """Part of the form validation process, overriding to apply logic to form fields
        and generate errors if some field values are not appropriate.

        This method is involved with form validation. Three types of cleaning methods are 
        run during form processing; and are run when the is_valid() method is called on
        an instance of the form. The added features here are responsible for identifying
        errors in the inputted ata, and applying them.
        """
        cleaned_data = super(ActionUpdateForm, self).clean()

        # Error checking: read error response for meaning behind each
        if cleaned_data.get("complete") == True and not cleaned_data.get("description_performed", "").strip():
            self._errors["description_performed"] = self.error_class(["Completed actions must describe the action which was undertaken"])

        return cleaned_data

# Define a formset of ActionUpdateForms
IncidentActionFormSet = modelformset_factory(models.IncidentAction, form=ActionUpdateForm, extra=0)



class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    # def __init__(self, *args, **kwargs):
    #     """Form initialization: hide the field required to put in the email address
    #     """
    #     super(CustomPasswordResetForm, self).__init__(*args, **kwargs)

    #     self.fields['email'].widget = HiddenInput()

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(
            email__iexact=email, is_active=True)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            email = loader.render_to_string(email_template_name, c)
            send_mail(subject, email, from_email, [user.email])