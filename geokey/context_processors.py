from django.conf import settings


def allowed_contributors(request):
    """Allows access to settings constants within templates."""
    _ = request  # PEP-8 compliance without reducing readability.
    default = ("true", "auth", "false")
    # return the value you want as a dictionary. you may add multiple values in there.
    if hasattr(settings, 'ALLOWED_CONTRIBUTORS'):
        return {'ALLOWED_CONTRIBUTORS': settings.ALLOWED_CONTRIBUTORS}
    else:
        return {'ALLOWED_CONTRIBUTORS': default}
