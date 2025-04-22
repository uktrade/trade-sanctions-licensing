import magic
from apply_for_a_licence.models import Licence
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest
from django.shortcuts import Http404, get_object_or_404
from django.utils import timezone


def get_mime_type(file: UploadedFile) -> str:
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(initial_pos)
    return mime_type


def is_ajax(request: HttpRequest) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def is_request_ratelimited(request: HttpRequest) -> bool:
    return getattr(request, "limited", False)


def update_last_activity_session_timestamp(request: HttpRequest) -> None:
    """
    Update the session timestamp to the current time
    """
    request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()


def get_licence_object(request: HttpRequest) -> Licence:
    licence_id = request.session["licence_id"]
    licence = get_object_or_404(Licence, pk=licence_id)
    if licence.user != request.user:
        raise Http404
    return licence
