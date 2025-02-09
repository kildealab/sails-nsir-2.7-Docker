from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url, urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site

import json

from incidents_nsir import forms as rforms

@csrf_protect
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=rforms.CustomPasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        # ADDED: If user is logged in, automatically populate with email address:
        if not request.user.is_anonymous():
            form = password_reset_form(initial={'email': request.user.email})
        else:
            form = password_reset_form()
    context = {
        'form': form,
        'user': request.user,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def password_reset_done(request,
                        template_name='registration/password_reset_done.html',
                        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                # Added to update user model:
                user.must_change_password = False
                user.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(None)
    else:
        validlink = False
        form = None
    context = {
        'form': form,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def password_reset_confirm_uidb36(request, uidb36=None, **kwargs):
    # Support old password reset URLs that used base36 encoded user IDs.
    # Remove in Django 1.7
    try:
      uidb64 = force_text(urlsafe_base64_encode(force_bytes(base36_to_int(uidb36))))
    except ValueError:
      uidb64 = '1' # dummy invalid ID (incorrect padding for base64)
    return password_reset_confirm(request, uidb64=uidb64, **kwargs)

def password_reset_complete(request,
                            template_name='registration/password_reset_complete.html',
                            current_app=None, extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL)
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


# @sensitive_post_parameters()
# @csrf_protect
# @login_required
# def password_change(request,
#                     template_name='registration/password_change_form.html',
#                     post_change_redirect=None,
#                     password_change_form=PasswordChangeForm,
#                     current_app=None, extra_context=None):
#     if post_change_redirect is None:
#         post_change_redirect = reverse('password_change_done')
#     else:
#         post_change_redirect = resolve_url(post_change_redirect)
#     if request.method == "POST":
#         form = password_change_form(user=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(post_change_redirect)
#     else:
#         form = password_change_form(user=request.user)
#     context = {
#         'form': form,
#     }
#     if extra_context is not None:
#         context.update(extra_context)
#     return TemplateResponse(request, template_name, context,
#                             current_app=current_app)

@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request, uidb64=None,
                    template_name='registration/password_change.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    # UserModel = get_user_model()
    # assert uidb64 is not None and token is not None  # checked by URLconf
    # try:
    #     uid = urlsafe_base64_decode(uidb64)
    #     user = UserModel._default_manager.get(pk=uid)
    # except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
    #     user = None
    user = request.user

    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        post_change_redirect = reverse('password_change_done')
        if form.is_valid():
            form.save()
            if user.must_change_password:
                user.must_change_password = False
                user.save()
            return HttpResponseRedirect(post_change_redirect)
        else:
            response_kwargs = {}
            response_kwargs['content_type'] = 'application/json'
            return HttpResponse(json.dumps(form.errors), **response_kwargs)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@login_required
def password_change_done(request,
                         template_name='registration/password_change_done.html',
                         current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)
