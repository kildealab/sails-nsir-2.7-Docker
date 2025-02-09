from django.conf import settings

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext as _

if len(settings.DATABASES) > 1:
    DATABASES = ['default','tax1']
else:
    DATABASES = ['default']

class ILSUser(AbstractUser):
    """Model used to represent a user of SaILS
    """
    # These will be included in the createsuperuser admin-command
    REQUIRED_FIELDS = ['first_name','last_name','email']

    class Meta:
        db_table = 'auth_user'
        ordering = ['last_name', 'first_name']

    #-------------------------------------------------------------------------------------
    # Model Fields
    #-------------------------------------------------------------------------------------
    # User can specify if want to receive notifications when the investigation/actions for
    # all Incidents the user is subscribed to. Note the keys tying an incident
    # subscription status to a user are stored in Subscription objects. Also note that
    # action_notifications encompasses learning and sharing actions.
    action_notifications = models.BooleanField(
        default=True,
        help_text="Subscribe to incident action notifications"
    )
    investigation_notifications = models.BooleanField(
        default=True,
        help_text="Subscribe to investigation assignment notifications"
    )

    # field which indicates if the user is a designated investigator
    is_investigator = models.BooleanField(
        default=False,
        help_text="Indicates whether or not ILSUser can be assigned to investigate incidents"
    )

    # field which indicates if the user is a radiation oncologist
    is_oncologist = models.BooleanField(
        default=False,
        help_text="Indicates whether or not ILSUser is an oncologist"
    )

    # field which lists the areas of expertise for an investigator: to be displayed when
    # allowing ILSUsers to select an investigator for a particular incident
    responsibilities = models.TextField(
        help_text="Areas of expertise for a particular investigator. Separate values by commas.",
        null=True,
        blank=True,
    )

    # field which indicates if the user must change their password before accessing other
    # site features.
    must_change_password = models.BooleanField(
        help_text="Parameter set to require users to change their password before engaging with other site functionality",
        default=True,
    )

    # ILS Users role within the department (e.g. physicist, therapist, etc)
    role = models.ForeignKey(
        "Role",
        help_text="Role of the individual within the department",
        verbose_name="Role",
        null=True,
        blank=True,
    )

    last_activity = models.DateTimeField(
        help_text="DateTime of the last activity of a user",
        null=True,
        blank=True,
    )

    def can_edit(self, investigator_pk):
        gate_editing = settings.GATE_EDITING
        investigator = ILSUser.objects.get(pk=investigator_pk)

        if self.is_superuser:
            return True
        else:
            if gate_editing and self != investigator:
                return False
            else:
                return True

    # Used in notifications App
    def can_investigate(self):
        return self.has_perm("incidents.change_investigation")

    # Save new users to all databases in the project
    def save(self, *args, **kwargs):
        for database in DATABASES:
            super(ILSUser, self).save(using=database)

    def get_name(self):
        return_string = ""
        if self.is_oncologist:
            return_string = 'Dr. %s %s' % (self.first_name, self.last_name)
        elif self.first_name and self.last_name:
            return_string = '%s %s' % (self.first_name, self.last_name)
        else:
            return_string = self.username
        if settings.ANONYMOUS_DISPLAY and not self.is_superuser:
            anon_string = "".join("*" for i in range(len(return_string)))
            return_string = anon_string
        return return_string

    # Set way in which ILSUsers are displayed in strings 
    def __unicode__(self):
        return self.get_name()

class AbstractChoice(models.Model):
    """Skeleton for models to be accessed via ILSUser model FK fields.

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
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Role(AbstractChoice):
    """Role of an ILSUser within a radiotherapy clinic
    """
    class Meta(AbstractChoice.Meta):
        #ordering = ('order',)
        verbose_name_plural = "roles"

# @receiver(pre_delete, sender=ILSUser)
# def ilsuser_delete(sender, instance, **kwargs):
#     print "**********************************DELETE******************************"
#     current_db = instance._state.db
#     for database in DATABASES:
#         if database != current_db:
#             other_instance = ILSUser.objects.using(database).get(instance.pk)
#             other_instance.delete()