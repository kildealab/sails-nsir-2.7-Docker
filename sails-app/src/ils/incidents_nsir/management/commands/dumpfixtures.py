from django.conf import settings
from django.core import management
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import dumpdata
import incidents_nsir.models
import os.path
import sys

class Command(BaseCommand):
    """This command may be run as an admin-command via python manage.py dumpfixtures --settings=ils.dev_settings
    for any project where the incidents_nsir app is installed.

    The command will create JSON fixture files for all the incidents_nsir models listed
    in the fixture_models array provided in the handle method. Note this will overwrite
    all equally-named fixture files already existing in the incidents_nsir fixture/ 
    directory.
    """
    help = 'Create fixture files for relevant models in the incidents_nsir app'

    def handle(self, *args, **options):
        fixture_models = [
            'AcuteMedicalHarm',
            'ActionReduceRisk',
            'AllowedTemplateField',
            'AmelioratingAction',
            'BodyRegionTreated',
            'ContributingFactor',
            'Diagnosis',
            'DosimetricImpact',
            'EventType',
            'FunctionalWorkArea',
            'IndividualDetected',
            'IndividualInvolved',
            'LatentMedicalHarm',
            'LocalSeverityLevel',
            'Month',
            'NumberPatientsAffected',
            'PatientGender',
            'ProblemType',
            'ProcessStepDetected',
            'ProcessStepOccurred',
            'RadiationTreatmentTechnique',
            'ReportType',
            'SafetyBarrierFailed',
            'SafetyBarrierPrevented',
            'SecondaryProblemType',
            'StatCompletionFilter',
            'StatDateBin',
            'StatDateType',
            'StatFKModelChoice',
            'StatParameterType',
            'StatPlotType',
            'StatUserChoice',
            'SupportRequired',
            'SupportGiven',
            'TimePeriodDetected',
            'TimePeriodOccurred',
            'TreatmentIntent',
        ]

        for model in fixture_models:
            filename = model + '.json'
            with open(settings.BASE_DIR+'/incidents_nsir/newfixtures/'+filename,'w') as f:
                if len(settings.DATABASES) > 1:
                    management.call_command('dumpdata', 'incidents_nsir.'+model, format="json", indent=2, database="tax1",stdout=f)        
                else:
                    management.call_command('dumpdata', 'incidents_nsir.'+model, format="json", indent=2, stdout=f)        


        # management.call_command('dumpdata', 'incidents_nsir.EventType', format="json", indent=2, database="tax1")        

        # for poll_id in args:
        #     try:
        #         poll = Poll.objects.get(pk=int(poll_id))
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write('Successfully closed poll "%s"' % poll_id)