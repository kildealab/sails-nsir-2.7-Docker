from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, ReadOnlyPasswordHashField
from . models import ILSUser, Role
from django import forms

# Use when accessing existing ILSUser
class ILSUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = ILSUser
    password = ReadOnlyPasswordHashField(
      label= ("Password"),
      help_text= ("Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"password/\">this form</a>."))


# Use when creating new ILSUser: handle potential duplication of usernames
class ILSUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = ILSUser

    def __init__(self, *args, **kwargs):
        super(ILSUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['role'].required = True

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            ILSUser.objects.get(username=username)
        except ILSUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


# Create instances of previous two classes. 
class ILSUserAdmin(UserAdmin):
    form = ILSUserChangeForm
    add_form = ILSUserCreationForm
    UserAdmin.fieldsets[3][1]["fields"] = UserAdmin.fieldsets[3][1]["fields"] + ('last_activity',)
    fieldsets = UserAdmin.fieldsets + (
        ("SaILS Fields", {'fields': ('is_investigator', 'is_oncologist', 'action_notifications', 'investigation_notifications', 'role', 'must_change_password')}),
    )
    add_fieldsets = (
        (None, {'fields':('username','password1','password2','first_name','last_name','email', 'role'),}),
    )

    list_display = ('__unicode__','first_name','last_name','email','role','is_investigator','is_oncologist','is_superuser','date_joined','last_activity')
    list_filter = ['role','is_investigator','is_oncologist','is_superuser']

    def link_to_change_form(self,obj):
        """If names are not provided, display the user ID number
        """
        if obj.first_name:
            return obj
        else:
            return "User #%d" % (obj.id)
    link_to_change_form.short_description = 'User'

#-----------------------------------------------------------------------------------------
# Following two classes are used for admin display of models without tree structure.
#-----------------------------------------------------------------------------------------
class NameSlugAdminMixin(object):
    prepopulated_fields = {"slug": ("name",)}
    pass

class NameSlugAdmin(NameSlugAdminMixin, admin.ModelAdmin):
    fields = ['name', 'slug', 'description','order']

nameslug_array = [
    Role,
]

admin.site.register(ILSUser, ILSUserAdmin)
admin.site.register(nameslug_array,NameSlugAdmin)