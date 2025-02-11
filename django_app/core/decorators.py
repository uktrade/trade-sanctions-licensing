from core.utils import update_last_activity_session_timestamp


def reset_last_activity_session_timestamp(view_func):
    """Decorator to reset the last activity session timestamp, refresh it."""

    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        update_last_activity_session_timestamp(request)
        return response

    return wrapper
