from functools import wraps

from django.conf import settings
from django.http import Http404


def is_demo_api_enabled() -> bool:
    return bool(
        getattr(settings, "MDC_DEMO_API_ENABLED", False)
        or getattr(settings, "DEBUG", False)
    )


def demo_api_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not is_demo_api_enabled():
            raise Http404
        return view_func(request, *args, **kwargs)

    return wrapped_view
