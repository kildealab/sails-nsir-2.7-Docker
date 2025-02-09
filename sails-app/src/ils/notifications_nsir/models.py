from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Subscription model. One user can have multiple subscriptions (i.e. one or zero subscriptions
# to each Incident in the database)
class Subscription(models.Model):
    """Model to represent a subscription of a particular ILSUser to a particular incident.

    Subscriptions between an ILSUser and an Incident are used when sending email
    notifications. An ILSUser may be subscribed to many Incidents, and an Incident may
    be subscribed by many ILSUsers.
    """
    user = models.ForeignKey(User)
    incident = models.ForeignKey('incidents_nsir.Incident', related_name="subscription", null=True, blank=True)

    def __unicode__(self):
        return "Subscription (%s, %s)" % (self.user.get_name(), self.incident.incident_id)

class ReminderType(models.Model):
    """Model to represent a reminder, that contains information on the frequency with
    which reminders should be sent to investigators of incomplete investigations.
    """

    name = models.CharField(max_length=255, null=True, blank=True,
        help_text="verbose name of the reminder type"
    )
    reminder_type = models.CharField(max_length=255, null=True, blank=True,
        help_text="code name of the reminder type- should not change"
    )
    frequency_days = models.PositiveIntegerField(null=True, blank=True,
        help_text="number of days that define the frequency of this reminder"
    )

    def __unicode__(self):
        return self.name