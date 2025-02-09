from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from django.db.models import Q

from notifications_nsir import signals
from notifications_nsir.models import ReminderType
from incidents_nsir import models

import datetime

logger = get_task_logger(__name__)

@periodic_task(
    # run_every=(crontab(minute=46, hour=16)),
    # run_every=(crontab(minute='*/2')),
    run_every=(crontab(minute=0,hour=7,day_of_week='*')),
    name="send_investigation_reminders",
    ignore_result=True
)
def send_investigation_reminders():
    """
    Send investigation reminder emails for those incident investigations which are
    incomplete after a perliminary time interval, then periodically after another time
    interval. 
    """
    try:
        first_reminder = ReminderType.objects.get(reminder_type="first")
        periodic_reminder = ReminderType.objects.get(reminder_type="periodic")

        current_date = datetime.datetime.now()
        first_threshold = current_date - datetime.timedelta(days=first_reminder.frequency_days)
        periodic_threshold = current_date - datetime.timedelta(days=periodic_reminder.frequency_days)

        incidents = models.Incident.incomplete.filter(
            Q(date_last_reminder__lte=first_threshold) |
            Q(date_last_reminder__isnull=True)
        )

        for incident in incidents:
            if len(incident.get_missing_field_ids_NOACTS()) > 0:
                if not incident.first_reminder_sent:
                    logger.info("Status of initial incident reminder for incident #%d :" % incident.incident_id)
                    incident.first_reminder_sent = True
                    incident.date_last_reminder = current_date
                    incident.save()
                    signals.investigation_reminder.send(sender=None, incident=incident)
                elif incident.date_last_reminder < periodic_threshold:
                    logger.info("Status of periodic incident reminder for incident #%d :" % incident.incident_id)
                    incident.date_last_reminder = current_date
                    incident.save()
                    signals.investigation_reminder.send(sender=None, incident=incident)
        logger.info("All necessary reminders sent.")
    
    except (AttributeError, TypeError, ReminderType.DoesNotExist):
        logger.info("Bad query to DB for frequency types, no emails sent.")


# @periodic_task(
#     # run_every=(crontab(minute=46, hour=16)),
#     # run_every=(crontab(minute='*/2')),
#     run_every=(crontab(minute=0,hour=7,day_of_week='*')),
#     # run_every=(crontab(minute=15,hour=11,day_of_week='*')),
#     name="send_action_reminders",
#     ignore_result=True
# )
# def send_action_reminders():
#     """
#     Send action reminder emails for those taskable actions which are
#     incomplete after a perliminary time interval, then periodically after another time
#     interval. 
#     """
#     try:
#         first_reminder = ReminderType.objects.get(reminder_type="first")
#         periodic_reminder = ReminderType.objects.get(reminder_type="periodic")
        
#         current_date = datetime.datetime.now()
#         first_threshold = current_date - datetime.timedelta(days=first_reminder.frequency_days)
#         periodic_threshold = current_date - datetime.timedelta(days=periodic_reminder.frequency_days)
        
#         actions = models.IncidentAction.objects.filter(
#             Q(complete=False) &
#             (
#                 Q(date_last_reminder__isnull=True) |
#                 Q(date_last_reminder__lte=first_threshold)
#             )
#         )
        
#         for action in actions:
#             if not action.first_reminder_sent:
#                 action.first_reminder_sent = True
#                 action.date_last_reminder = current_date
#                 action.save()
#                 signals.action_reminder.send(sender=None, action=action)
#                 logger.info("Sent initial email reminder for action #%d (incident #%d)" % (action.action_id,action.incident.incident_id))
#             elif action.date_last_reminder < periodic_threshold:
#                 action.date_last_reminder = current_date
#                 action.save()
#                 signals.action_reminder.send(sender=None, action=action)
#                 logger.info("Sent periodic email reminder for action #%d (incident #%d)" % (action.action_id,action.incident.incident_id))
#         logger.info("All necessary reminders sent.")
    
#     except (AttributeError, TypeError, ReminderType.DoesNotExist):
#         logger.info("Bad query to DB for frequency types, no emails sent.")