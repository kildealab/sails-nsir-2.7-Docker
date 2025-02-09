from django.utils import timezone

from accounts.models import ILSUser

from django.http import HttpResponseRedirect

class updatelastvisit(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Update the datetime of last activity for the current user upon any sending of HTTP Request, including AJAX.
        """
        assert hasattr(request, 'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated():
            ILSUser.objects.filter(id=request.user.id) \
                           .update(last_activity=timezone.now())
            cur_user = ILSUser.objects.get(id=request.user.id)

            cur_user.save()

class RequestMiddleWare():
    def process_request(self,request):
        """Determine if the request has been made via Internet Explorer.
        """
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT'].lower()
            if 'msie' in user_agent:
                request.is_IE = True
            else:
                request.is_IE = False

        return None

class AjaxRedirect(object):
    def process_response(self, request, response):
        """Required to allow and AJAX post to redirect to another page (used in the change
        event type behaviour).
        """
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = 278
        return response