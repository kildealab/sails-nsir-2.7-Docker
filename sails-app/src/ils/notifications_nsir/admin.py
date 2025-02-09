from django.contrib import admin
from adminsortable.admin import SortableAdminMixin
from import_export.admin import ExportMixin

from . import models

class SubscriptionAdmin(admin.ModelAdmin):
    fields = ['user', 'incident']
    list_display = ('__unicode__','user','incident')

class ReminderTypeAdmin(admin.ModelAdmin):
    fields = ['name', 'reminder_type', 'frequency_days']
    list_display = ('__unicode__','frequency_days')

admin.site.register(models.ReminderType, ReminderTypeAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)