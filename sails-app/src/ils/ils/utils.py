from django.contrib.auth import  get_user_model
from django.db.models import Q

def get_users_by_permission_q(permission_name, include_superusers=True):
    """ Returns the Q object suitable for querying users by permission. If include_superusers
    is true (default) all superusers will be also included. Otherwise
    only users with explicitely set permissions will be included. """
    (appname, codename) = permission_name.split(".")

    query = \
        Q(user_permissions__codename=codename, user_permissions__content_type__app_label=appname) | \
        Q(groups__permissions__codename=codename, groups__permissions__content_type__app_label=appname)

    if include_superusers:
        query |= Q(is_superuser=True)

    # The above query may return multiple instances of User objects if user
    # has overlapping permissions. Hence we are using a nested query by unique
    # user ids.
    return {'pk__in': get_user_model().objects.filter(query).distinct().values_list('pk', flat=True)}

def get_users_by_permission(permission_name, include_superusers=True):
    """ Returns the queryset of User objects with the given permission. Permission name
    is in the form appname.permission similar to the format
    required by django.contrib.auth.decorators.permission_required
    """
    return get_user_model().objects.filter(**get_users_by_permission_q(permission_name, include_superusers) )
