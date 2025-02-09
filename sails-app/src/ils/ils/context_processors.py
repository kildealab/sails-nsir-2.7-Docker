from django.conf import settings

# Context variables which are passed to all templates in the project
def info(request):
    return {
        "VERSION": settings.VERSION,
        "BUG_REPORT_URL": settings.BUG_REPORT_URL,
        "MAX_CACHE_TIMEOUT": settings.MAX_CACHE_TIMEOUT,
        "FORCE_SCRIPT_NAME": settings.FORCE_SCRIPT_NAME,
        "CONTACT_EMAIL": settings.CONTACT_EMAIL,
        "BASE_TEMPLATE": settings.BASE_TEMPLATE,
        "ANONYMOUS_DISPLAY": settings.ANONYMOUS_DISPLAY,
        "PHP_DIR": settings.PHP_DIR,
        "TUTORIALS": settings.TUTORIALS
    }
