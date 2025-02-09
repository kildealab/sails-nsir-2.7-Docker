# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Incident'
        db.create_table(u'incidents_nsir_incident', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('incident_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('reportable_circumstance', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('near_miss', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('acute_medical_harm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.AcuteMedicalHarm'], null=True, blank=True)),
            ('dosimetric_impact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.DosimetricImpact'], null=True, blank=True)),
            ('latent_medical_harm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.LatentMedicalHarm'], null=True, blank=True)),
            ('functional_work_area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.FunctionalWorkArea'], null=True, blank=True)),
            ('date_incident_detected', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('date_incident_occurred', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('time_period_detected', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.TimePeriodDetected'], null=True, blank=True)),
            ('time_period_occurred', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.TimePeriodOccurred'], null=True, blank=True)),
            ('patient_month_birth', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('patient_year_birth', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('patient_gender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.PatientGender'], null=True, blank=True)),
            ('diagnosis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.Diagnosis'], null=True, blank=True)),
            ('process_step_occurred', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.ProcessStepOccurred'], null=True, blank=True)),
            ('process_step_detected', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.ProcessStepDetected'], null=True, blank=True)),
            ('problem_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.ProblemType'], null=True, blank=True)),
            ('secondary_problem_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.SecondaryProblemType'], null=True, blank=True)),
            ('contributing_factors', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.ContributingFactor'], null=True, blank=True)),
            ('number_patients_affected', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.NumberPatientsAffected'], null=True, blank=True)),
            ('radiation_treatment_technique', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.RadiationTreatmentTechnique'], null=True, blank=True)),
            ('total_dose_prescribed', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=2, blank=True)),
            ('number_fractions_prescribed', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('number_fractions_incorrect', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('hardware_manufacturer_model', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('softwareware_manufacturer_model', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('treatment_intent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['incidents_nsir.TreatmentIntent'], null=True, blank=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['Incident'])

        # Adding M2M table for field individual_detected on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_individual_detected')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('individualdetected', models.ForeignKey(orm[u'incidents_nsir.individualdetected'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'individualdetected_id'])

        # Adding M2M table for field individual_involved on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_individual_involved')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('individualinvolved', models.ForeignKey(orm[u'incidents_nsir.individualinvolved'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'individualinvolved_id'])

        # Adding M2M table for field body_region_treated on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_body_region_treated')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('bodyregiontreated', models.ForeignKey(orm[u'incidents_nsir.bodyregiontreated'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'bodyregiontreated_id'])

        # Adding M2M table for field ameliorating_actions on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_ameliorating_actions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('amelioratingaction', models.ForeignKey(orm[u'incidents_nsir.amelioratingaction'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'amelioratingaction_id'])

        # Adding M2M table for field safety_barriers_failed on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_safety_barriers_failed')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('safetybarrierfailed', models.ForeignKey(orm[u'incidents_nsir.safetybarrierfailed'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'safetybarrierfailed_id'])

        # Adding M2M table for field safety_barriers_prevented on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_safety_barriers_prevented')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('safetybarrierprevented', models.ForeignKey(orm[u'incidents_nsir.safetybarrierprevented'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'safetybarrierprevented_id'])

        # Adding M2M table for field actions_reduce_risk on 'Incident'
        m2m_table_name = db.shorten_name(u'incidents_nsir_incident_actions_reduce_risk')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('incident', models.ForeignKey(orm[u'incidents_nsir.incident'], null=False)),
            ('actionreducerisk', models.ForeignKey(orm[u'incidents_nsir.actionreducerisk'], null=False))
        ))
        db.create_unique(m2m_table_name, ['incident_id', 'actionreducerisk_id'])

        # Adding model 'AcuteMedicalHarm'
        db.create_table(u'incidents_nsir_acutemedicalharm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['AcuteMedicalHarm'])

        # Adding model 'DosimetricImpact'
        db.create_table(u'incidents_nsir_dosimetricimpact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['DosimetricImpact'])

        # Adding model 'LatentMedicalHarm'
        db.create_table(u'incidents_nsir_latentmedicalharm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['LatentMedicalHarm'])

        # Adding model 'FunctionalWorkArea'
        db.create_table(u'incidents_nsir_functionalworkarea', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['FunctionalWorkArea'])

        # Adding model 'TimePeriodDetected'
        db.create_table(u'incidents_nsir_timeperioddetected', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['TimePeriodDetected'])

        # Adding model 'TimePeriodOccurred'
        db.create_table(u'incidents_nsir_timeperiodoccurred', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['TimePeriodOccurred'])

        # Adding model 'IndividualDetected'
        db.create_table(u'incidents_nsir_individualdetected', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['IndividualDetected'])

        # Adding model 'IndividualInvolved'
        db.create_table(u'incidents_nsir_individualinvolved', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['IndividualInvolved'])

        # Adding model 'PatientGender'
        db.create_table(u'incidents_nsir_patientgender', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['PatientGender'])

        # Adding model 'Diagnosis'
        db.create_table(u'incidents_nsir_diagnosis', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['Diagnosis'])

        # Adding model 'ProcessStepOccurred'
        db.create_table(u'incidents_nsir_processstepoccurred', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['ProcessStepOccurred'])

        # Adding model 'ProcessStepDetected'
        db.create_table(u'incidents_nsir_processstepdetected', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['ProcessStepDetected'])

        # Adding model 'ProblemType'
        db.create_table(u'incidents_nsir_problemtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.ProblemType'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['ProblemType'])

        # Adding model 'SecondaryProblemType'
        db.create_table(u'incidents_nsir_secondaryproblemtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.SecondaryProblemType'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['SecondaryProblemType'])

        # Adding model 'ContributingFactor'
        db.create_table(u'incidents_nsir_contributingfactor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.ContributingFactor'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['ContributingFactor'])

        # Adding model 'NumberPatientsAffected'
        db.create_table(u'incidents_nsir_numberpatientsaffected', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['NumberPatientsAffected'])

        # Adding model 'RadiationTreatmentTechnique'
        db.create_table(u'incidents_nsir_radiationtreatmenttechnique', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['RadiationTreatmentTechnique'])

        # Adding model 'BodyRegionTreated'
        db.create_table(u'incidents_nsir_bodyregiontreated', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['BodyRegionTreated'])

        # Adding model 'TreatmentIntent'
        db.create_table(u'incidents_nsir_treatmentintent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'incidents_nsir', ['TreatmentIntent'])

        # Adding model 'AmelioratingAction'
        db.create_table(u'incidents_nsir_amelioratingaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.AmelioratingAction'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['AmelioratingAction'])

        # Adding model 'SafetyBarrierFailed'
        db.create_table(u'incidents_nsir_safetybarrierfailed', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.SafetyBarrierFailed'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['SafetyBarrierFailed'])

        # Adding model 'SafetyBarrierPrevented'
        db.create_table(u'incidents_nsir_safetybarrierprevented', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.SafetyBarrierPrevented'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['SafetyBarrierPrevented'])

        # Adding model 'ActionReduceRisk'
        db.create_table(u'incidents_nsir_actionreducerisk', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, unique=True, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='children', to=orm['incidents_nsir.ActionReduceRisk'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'incidents_nsir', ['ActionReduceRisk'])


    def backwards(self, orm):
        # Deleting model 'Incident'
        db.delete_table(u'incidents_nsir_incident')

        # Removing M2M table for field individual_detected on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_individual_detected'))

        # Removing M2M table for field individual_involved on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_individual_involved'))

        # Removing M2M table for field body_region_treated on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_body_region_treated'))

        # Removing M2M table for field ameliorating_actions on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_ameliorating_actions'))

        # Removing M2M table for field safety_barriers_failed on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_safety_barriers_failed'))

        # Removing M2M table for field safety_barriers_prevented on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_safety_barriers_prevented'))

        # Removing M2M table for field actions_reduce_risk on 'Incident'
        db.delete_table(db.shorten_name(u'incidents_nsir_incident_actions_reduce_risk'))

        # Deleting model 'AcuteMedicalHarm'
        db.delete_table(u'incidents_nsir_acutemedicalharm')

        # Deleting model 'DosimetricImpact'
        db.delete_table(u'incidents_nsir_dosimetricimpact')

        # Deleting model 'LatentMedicalHarm'
        db.delete_table(u'incidents_nsir_latentmedicalharm')

        # Deleting model 'FunctionalWorkArea'
        db.delete_table(u'incidents_nsir_functionalworkarea')

        # Deleting model 'TimePeriodDetected'
        db.delete_table(u'incidents_nsir_timeperioddetected')

        # Deleting model 'TimePeriodOccurred'
        db.delete_table(u'incidents_nsir_timeperiodoccurred')

        # Deleting model 'IndividualDetected'
        db.delete_table(u'incidents_nsir_individualdetected')

        # Deleting model 'IndividualInvolved'
        db.delete_table(u'incidents_nsir_individualinvolved')

        # Deleting model 'PatientGender'
        db.delete_table(u'incidents_nsir_patientgender')

        # Deleting model 'Diagnosis'
        db.delete_table(u'incidents_nsir_diagnosis')

        # Deleting model 'ProcessStepOccurred'
        db.delete_table(u'incidents_nsir_processstepoccurred')

        # Deleting model 'ProcessStepDetected'
        db.delete_table(u'incidents_nsir_processstepdetected')

        # Deleting model 'ProblemType'
        db.delete_table(u'incidents_nsir_problemtype')

        # Deleting model 'SecondaryProblemType'
        db.delete_table(u'incidents_nsir_secondaryproblemtype')

        # Deleting model 'ContributingFactor'
        db.delete_table(u'incidents_nsir_contributingfactor')

        # Deleting model 'NumberPatientsAffected'
        db.delete_table(u'incidents_nsir_numberpatientsaffected')

        # Deleting model 'RadiationTreatmentTechnique'
        db.delete_table(u'incidents_nsir_radiationtreatmenttechnique')

        # Deleting model 'BodyRegionTreated'
        db.delete_table(u'incidents_nsir_bodyregiontreated')

        # Deleting model 'TreatmentIntent'
        db.delete_table(u'incidents_nsir_treatmentintent')

        # Deleting model 'AmelioratingAction'
        db.delete_table(u'incidents_nsir_amelioratingaction')

        # Deleting model 'SafetyBarrierFailed'
        db.delete_table(u'incidents_nsir_safetybarrierfailed')

        # Deleting model 'SafetyBarrierPrevented'
        db.delete_table(u'incidents_nsir_safetybarrierprevented')

        # Deleting model 'ActionReduceRisk'
        db.delete_table(u'incidents_nsir_actionreducerisk')


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
            'softwareware_manufacturer_model': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
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