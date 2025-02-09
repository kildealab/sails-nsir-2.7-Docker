# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Incident.predefined_type'
        db.alter_column(u'incidents_nsir_incident', 'predefined_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.PredefinedIncident'], null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):

        # Changing field 'Incident.predefined_type'
        db.alter_column(u'incidents_nsir_incident', 'predefined_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.PredefinedIncident'], null=True))

    models = {
        u'accounts.ilsuser': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'ILSUser', 'db_table': "'auth_user'"},
            'action_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'investigation_notifications': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_oncologist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_activity': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'must_change_password': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'responsibilities': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.Role']", 'null': 'True', 'blank': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'accounts.role': {
            'Meta': {'ordering': "['name']", 'object_name': 'Role'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'incidents_nsir.actionreducerisk': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ActionReduceRisk'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.ActionReduceRisk']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.acutemedicalharm': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'AcuteMedicalHarm'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.allowedtemplatefield': {
            'Meta': {'ordering': "['field_name']", 'object_name': 'AllowedTemplateField'},
            'event_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['incidents_nsir.EventType']", 'symmetrical': 'False'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'incidents_nsir.amelioratingaction': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'AmelioratingAction'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.AmelioratingAction']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.bodyregiontreated': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'BodyRegionTreated'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.contributingfactor': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ContributingFactor'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.ContributingFactor']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.diagnosis': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'Diagnosis'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.dosimetricimpact': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'DosimetricImpact'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.eventtype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'EventType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.functionalworkarea': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'FunctionalWorkArea'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.incident': {
            'Meta': {'ordering': "('-submitted',)", 'object_name': 'Incident'},
            'actions_reduce_risk': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.ActionReduceRisk']", 'null': 'True', 'blank': 'True'}),
            'acute_medical_harm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.AcuteMedicalHarm']", 'null': 'True', 'blank': 'True'}),
            'ameliorating_actions': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.AmelioratingAction']", 'null': 'True', 'blank': 'True'}),
            'body_region_treated': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.BodyRegionTreated']", 'null': 'True', 'blank': 'True'}),
            'contributing_factors': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.ContributingFactor']", 'null': 'True', 'blank': 'True'}),
            'date_incident_detected': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_incident_occurred': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_last_reminder': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'descriptor': ('django.db.models.fields.TextField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'diagnosis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Diagnosis']", 'null': 'True', 'blank': 'True'}),
            'discussion': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'dosimetric_impact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.DosimetricImpact']", 'null': 'True', 'blank': 'True'}),
            'duplicate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Incident']", 'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.EventType']", 'null': 'True', 'blank': 'True'}),
            'first_reminder_sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'functional_work_area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.FunctionalWorkArea']", 'null': 'True', 'blank': 'True'}),
            'hardware_manufacturer_model': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hospital_form_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'incident_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'individual_detected': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.IndividualDetected']", 'null': 'True', 'blank': 'True'}),
            'individual_involved': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.IndividualInvolved']", 'null': 'True', 'blank': 'True'}),
            'invalid_reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'investigation_assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.ILSUser']", 'null': 'True', 'blank': 'True'}),
            'investigation_assigned_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'investigation_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'investigation_completed_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'investigation_narrative': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'investigator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incident_assigned_to_investigator'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'latent_medical_harm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.LatentMedicalHarm']", 'null': 'True', 'blank': 'True'}),
            'near_miss': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'number_fractions_incorrect': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_fractions_prescribed': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_patients_affected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.NumberPatientsAffected']", 'null': 'True', 'blank': 'True'}),
            'oncologist': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incident_assigned_to_oncologist'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'patient_gender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.PatientGender']", 'null': 'True', 'blank': 'True'}),
            'patient_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'patient_month_birth': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Month']", 'null': 'True', 'blank': 'True'}),
            'patient_support_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'patient_support_given': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'patient_support_given'", 'null': 'True', 'to': u"orm['incidents_nsir.SupportGiven']"}),
            'patient_support_required': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'patient_support_required'", 'null': 'True', 'to': u"orm['incidents_nsir.SupportRequired']"}),
            'patient_year_birth': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'predefined_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.PredefinedIncident']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'problem_type': ('mptt.fields.TreeForeignKey', [], {'to': u"orm['incidents_nsir.ProblemType']", 'null': 'True', 'blank': 'True'}),
            'process_step_detected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ProcessStepDetected']", 'null': 'True', 'blank': 'True'}),
            'process_step_occurred': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ProcessStepOccurred']", 'null': 'True', 'blank': 'True'}),
            'radiation_treatment_technique': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.RadiationTreatmentTechnique']", 'null': 'True', 'blank': 'True'}),
            'report_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ReportType']", 'null': 'True', 'blank': 'True'}),
            'reportable_circumstance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reported_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'reported_to': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'safety_barriers_failed': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.SafetyBarrierFailed']", 'null': 'True', 'blank': 'True'}),
            'safety_barriers_prevented': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.SafetyBarrierPrevented']", 'null': 'True', 'blank': 'True'}),
            'secondary_problem_type': ('mptt.fields.TreeManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.SecondaryProblemType']", 'null': 'True', 'blank': 'True'}),
            'software_manufacturer_model': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'submitted_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incident_submitted_by'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'support_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'support_given': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'staff_support_given'", 'null': 'True', 'to': u"orm['incidents_nsir.SupportGiven']"}),
            'support_required': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'staff_support_required'", 'null': 'True', 'to': u"orm['incidents_nsir.SupportRequired']"}),
            'time_detected': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_occurred': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_period_detected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TimePeriodDetected']", 'null': 'True', 'blank': 'True'}),
            'time_period_occurred': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TimePeriodOccurred']", 'null': 'True', 'blank': 'True'}),
            'total_dose_prescribed': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'treatment_intent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TreatmentIntent']", 'null': 'True', 'blank': 'True'}),
            'treatment_site': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'valid_status_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incident_valid_status_by'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'valid_status_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.incidentaction': {
            'Meta': {'object_name': 'IncidentAction'},
            'action_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_assigned_action'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_completed_action'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'date_assigned': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description_performed': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_proposed': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Incident']"}),
            'responsible': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'user_responsible_action'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"})
        },
        u'incidents_nsir.incidentsharing': {
            'Meta': {'object_name': 'IncidentSharing'},
            'assigned': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incidentsharing_assigned'", 'to': u"orm['accounts.ILSUser']"}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'done_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Incident']"}),
            'responsible': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'incidentsharing'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'sharing_audience': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.SharingAudience']"})
        },
        u'incidents_nsir.individualdetected': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'IndividualDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.individualinvolved': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'IndividualInvolved'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.investigation': {
            'Meta': {'object_name': 'Investigation'},
            'assigned': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'assigned_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'incidents_assigned'", 'null': 'True', 'to': u"orm['accounts.ILSUser']"}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['incidents_nsir.Incident']", 'unique': 'True'})
        },
        u'incidents_nsir.latentmedicalharm': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'LatentMedicalHarm'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.month': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'Month'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.numberpatientsaffected': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'NumberPatientsAffected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.oncologist': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Oncologist'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.patientgender': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'PatientGender'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.predefinedfield': {
            'Meta': {'object_name': 'PredefinedField'},
            'field_value': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.PredefinedIncident']"}),
            'model_field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.AllowedTemplateField']"})
        },
        u'incidents_nsir.predefinedincident': {
            'Meta': {'object_name': 'PredefinedIncident'},
            'code_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'predefined_created_by'", 'to': u"orm['accounts.ILSUser']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'incidents_nsir.problemtype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ProblemType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.ProblemType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.processstepdetected': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ProcessStepDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.processstepoccurred': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ProcessStepOccurred'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.radiationtreatmenttechnique': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'RadiationTreatmentTechnique'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.reporttype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'ReportType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.safetybarrierfailed': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SafetyBarrierFailed'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.SafetyBarrierFailed']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.safetybarrierprevented': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SafetyBarrierPrevented'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.SafetyBarrierPrevented']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.secondaryproblemtype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SecondaryProblemType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['incidents_nsir.SecondaryProblemType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.sharingaudience': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SharingAudience'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statcompletionfilter': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatCompletionFilter'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statdatebin': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatDateBin'},
            'bin_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statdatetype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatDateType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statfkmodelchoice': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatFKModelChoice'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statparametertype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatParameterType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'type_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statplottype': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatPlotType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'type_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.statuserchoice': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'StatUserChoice'},
            'account_field_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_field_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.supportgiven': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SupportGiven'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.supportrequired': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'SupportRequired'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.timeperioddetected': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'TimePeriodDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.timeperiodoccurred': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'TimePeriodOccurred'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.treatmentintent': {
            'Meta': {'ordering': "['order', 'name']", 'object_name': 'TreatmentIntent'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['incidents_nsir']