# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Incident.softwareware_manufacturer_model'
        db.delete_column(u'incidents_nsir_incident', 'softwareware_manufacturer_model')

        # Adding field 'Incident.software_manufacturer_model'
        db.add_column(u'incidents_nsir_incident', 'software_manufacturer_model',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Incident.softwareware_manufacturer_model'
        db.add_column(u'incidents_nsir_incident', 'softwareware_manufacturer_model',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Deleting field 'Incident.software_manufacturer_model'
        db.delete_column(u'incidents_nsir_incident', 'software_manufacturer_model')


    models = {
        u'incidents_nsir.actionreducerisk': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ActionReduceRisk'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.ActionReduceRisk']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.acutemedicalharm': {
            'Meta': {'ordering': "('order',)", 'object_name': 'AcuteMedicalHarm'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.amelioratingaction': {
            'Meta': {'ordering': "('order',)", 'object_name': 'AmelioratingAction'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.AmelioratingAction']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.bodyregiontreated': {
            'Meta': {'ordering': "('order',)", 'object_name': 'BodyRegionTreated'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.contributingfactor': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ContributingFactor'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.ContributingFactor']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.diagnosis': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Diagnosis'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.dosimetricimpact': {
            'Meta': {'ordering': "('order',)", 'object_name': 'DosimetricImpact'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.functionalworkarea': {
            'Meta': {'ordering': "('order',)", 'object_name': 'FunctionalWorkArea'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.incident': {
            'Meta': {'object_name': 'Incident'},
            'actions_reduce_risk': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.ActionReduceRisk']", 'null': 'True', 'blank': 'True'}),
            'acute_medical_harm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.AcuteMedicalHarm']", 'null': 'True', 'blank': 'True'}),
            'ameliorating_actions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.AmelioratingAction']", 'null': 'True', 'blank': 'True'}),
            'body_region_treated': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.BodyRegionTreated']", 'null': 'True', 'blank': 'True'}),
            'contributing_factors': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ContributingFactor']", 'null': 'True', 'blank': 'True'}),
            'date_incident_detected': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_incident_occurred': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'diagnosis': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.Diagnosis']", 'null': 'True', 'blank': 'True'}),
            'dosimetric_impact': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.DosimetricImpact']", 'null': 'True', 'blank': 'True'}),
            'functional_work_area': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.FunctionalWorkArea']", 'null': 'True', 'blank': 'True'}),
            'hardware_manufacturer_model': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incident_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'individual_detected': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.IndividualDetected']", 'null': 'True', 'blank': 'True'}),
            'individual_involved': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.IndividualInvolved']", 'null': 'True', 'blank': 'True'}),
            'latent_medical_harm': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.LatentMedicalHarm']", 'null': 'True', 'blank': 'True'}),
            'near_miss': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'number_fractions_incorrect': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_fractions_prescribed': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_patients_affected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.NumberPatientsAffected']", 'null': 'True', 'blank': 'True'}),
            'patient_gender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.PatientGender']", 'null': 'True', 'blank': 'True'}),
            'patient_month_birth': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'patient_year_birth': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'}),
            'problem_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ProblemType']", 'null': 'True', 'blank': 'True'}),
            'process_step_detected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ProcessStepDetected']", 'null': 'True', 'blank': 'True'}),
            'process_step_occurred': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.ProcessStepOccurred']", 'null': 'True', 'blank': 'True'}),
            'radiation_treatment_technique': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.RadiationTreatmentTechnique']", 'null': 'True', 'blank': 'True'}),
            'reportable_circumstance': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'safety_barriers_failed': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.SafetyBarrierFailed']", 'null': 'True', 'blank': 'True'}),
            'safety_barriers_prevented': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['incidents_nsir.SafetyBarrierPrevented']", 'null': 'True', 'blank': 'True'}),
            'secondary_problem_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.SecondaryProblemType']", 'null': 'True', 'blank': 'True'}),
            'software_manufacturer_model': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_period_detected': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TimePeriodDetected']", 'null': 'True', 'blank': 'True'}),
            'time_period_occurred': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TimePeriodOccurred']", 'null': 'True', 'blank': 'True'}),
            'total_dose_prescribed': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '2', 'blank': 'True'}),
            'treatment_intent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['incidents_nsir.TreatmentIntent']", 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.individualdetected': {
            'Meta': {'ordering': "('order',)", 'object_name': 'IndividualDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.individualinvolved': {
            'Meta': {'ordering': "('order',)", 'object_name': 'IndividualInvolved'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.latentmedicalharm': {
            'Meta': {'ordering': "('order',)", 'object_name': 'LatentMedicalHarm'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.numberpatientsaffected': {
            'Meta': {'ordering': "('order',)", 'object_name': 'NumberPatientsAffected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.patientgender': {
            'Meta': {'ordering': "('order',)", 'object_name': 'PatientGender'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.problemtype': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ProblemType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.ProblemType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.processstepdetected': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ProcessStepDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.processstepoccurred': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ProcessStepOccurred'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.radiationtreatmenttechnique': {
            'Meta': {'ordering': "('order',)", 'object_name': 'RadiationTreatmentTechnique'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.safetybarrierfailed': {
            'Meta': {'ordering': "('order',)", 'object_name': 'SafetyBarrierFailed'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.SafetyBarrierFailed']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.safetybarrierprevented': {
            'Meta': {'ordering': "('order',)", 'object_name': 'SafetyBarrierPrevented'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.SafetyBarrierPrevented']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.secondaryproblemtype': {
            'Meta': {'ordering': "('order',)", 'object_name': 'SecondaryProblemType'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'to': u"orm['incidents_nsir.SecondaryProblemType']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'incidents_nsir.timeperioddetected': {
            'Meta': {'ordering': "('order',)", 'object_name': 'TimePeriodDetected'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.timeperiodoccurred': {
            'Meta': {'ordering': "('order',)", 'object_name': 'TimePeriodOccurred'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'incidents_nsir.treatmentintent': {
            'Meta': {'ordering': "('order',)", 'object_name': 'TreatmentIntent'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['incidents_nsir']