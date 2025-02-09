from django.contrib import messages
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic import DeleteView, View

from . import models
from incidents_nsir.models import Incident
from incidents_nsir.views import LoginRequiredMixin

#*****************************************************************************************
# These views can be accessed directly using the URLconfs defined in urls.py, or more
# commonly, using the Subscribe/Unsubscribe links provided on each Incident page.
#*****************************************************************************************

class Subscribe(View):
    """View used to subscribe the current user to a particular incident.
    """
    template_name_suffix = "_create"
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        """Create the Subscription object and webpage for particular incident.

        Redirect the user to the investigation page to which they are subscribing, and
        display a message indicating that they have subscribed successfully or that they
        were already subscribed.
        """
        incident_id = self.kwargs['incident_id']
        my_inc = Incident.objects.get(incident_id=incident_id)
        inc_pk = my_inc.pk
        print inc_pk
        print self.request.user
        sub_instance, was_created = models.Subscription.objects.get_or_create(user=self.request.user, incident=my_inc)
        if was_created:
            messages.success(request, "You are now subscribed to Incident %s" % incident_id)
        else:
            messages.warning(request, "You are already subscribed to Incident %s" % incident_id)

        # Redirect user to the URL of the incident they subscribed to.
        return HttpResponseRedirect(reverse("incidents_nsir:incident", kwargs={"incident_id":incident_id}))


class Unsubscribe(LoginRequiredMixin, DeleteView):
    """View used to subscribe the current user from a particular incident.
    """
    model = models.Subscription

    def get(self, request, *args, **kwargs):
        """Delete the Subscription object and webpage for particular incident.

        Redirect the user to the investigation page to which they are subscribing, and
        display a message indicating that they have unsubscribed successfully or that they
        were not previously subscribed.
        """
        # if self.request.user.is_anonymous():
        #     return HttpResponseRedirect(reverse("login"))

        try:
            return super(Unsubscribe, self).get(self,request)
        except ObjectDoesNotExist: # I.e. no subscription matching this
            print self.kwargs["incident_id"]
            try:
                Incident.objects.get(incident_id=self.kwargs["incident_id"])
                return render(request, "notifications_nsir/no_subscription.html", {'incident_id': self.kwargs["incident_id"], 'exists': True})
            except ObjectDoesNotExist:
                return render(request, "notifications_nsir/no_subscription.html", {'incident_id': self.kwargs["incident_id"], 'exists': False})

    def get_object(self, *args, **kwargs):
        """Get the subscription object associated with a given ILSUser and Incident.
        """
        incident_id = self.kwargs["incident_id"]
        my_inc = Incident.objects.get(incident_id=incident_id)
        inc_pk = my_inc.pk
        obj = models.Subscription.objects.get(user=self.request.user, incident=inc_pk)
        return obj

    def get_success_url(self):
        """Define the URL to be accessed upon successful unsubscription.
        """
        if "cancel" not in self.request.POST:
            messages.success(self.request, "Successfully unsubscribed from Incident #%d" % (self.object.incident.incident_id))

        if self.request.POST.get("next", None) == "incident":
            return reverse("incidents_nsir:incident", kwargs={"incident_id":self.kwargs['incident_id']})
        elif self.request.user.is_investigator:
            return reverse("incidents_nsir:dashboard")

        return reverse("incidents_nsir:report")

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.get_success_url())

        return super(Unsubscribe, self).post(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(Unsubscribe, self).get_context_data(*args, **kwargs)
        context["next"] = self.request.GET.get("next", None)
        return context


