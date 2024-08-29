import logging
import uuid
from typing import Any

from apply_for_a_licence.forms import forms_documents as forms
from core.document_storage import TemporaryDocumentStorage
from core.utils import is_ajax
from core.views.base_views import BaseFormView
from django.core.cache import cache
from django.forms import Form
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from utils.s3 import (
    generate_presigned_url,
    get_all_session_files,
    get_user_uploaded_files,
)

logger = logging.getLogger(__name__)


class UploadDocumentsView(BaseFormView):
    """View for uploading documents.
    Accepts both Ajax and non-Ajax requests, to accommodate both JS and non-JS users respectively."""

    form_class = forms.UploadDocumentsForm
    template_name = "apply_for_a_licence/form_steps/upload_documents.html"
    file_storage = TemporaryDocumentStorage()
    success_url = reverse_lazy("check_your_answers")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Retrieve the already uploaded files from the session storage and add them to the context."""
        context = super().get_context_data(**kwargs)
        if session_files := get_all_session_files(TemporaryDocumentStorage(), self.request.session):
            context["session_files"] = session_files
        return context

    def form_valid(self, form: Form) -> HttpResponse:
        """Loop through the files and save them to the temporary storage. If the request is Ajax, return a JsonResponse.

        If the request is not Ajax, redirect to the summary page (the next step in the form)."""
        for temporary_file in form.cleaned_data["document"]:
            # adding the file name to the cache, so we can retrieve it later and confirm they uploaded it
            # we add a unique identifier to the key, so we do not overwrite previous uploads
            redis_cache_key = f"{self.request.session.session_key}{uuid.uuid4()}"
            cache.set(redis_cache_key, temporary_file.original_name)

            if is_ajax(self.request):
                # if it's an AJAX request, then files are sent to this view one at a time, so we can return a response
                # immediately, and not at the end of the for-loop
                return JsonResponse(
                    {
                        "success": True,
                        "file_name": temporary_file.original_name,
                    },
                    status=201,
                )
        if is_ajax(self.request):
            return JsonResponse({"success": True}, status=200)
        else:
            return super().form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        if is_ajax(self.request):
            return JsonResponse(
                {"success": False, "error": form.errors["document"][0], "file_name": self.request.FILES["document"].name},
                status=200,
            )
        else:
            return super().form_invalid(form)


class DeleteDocumentsView(View):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        if file_name := self.request.GET.get("file_name"):
            object_key = f"{self.request.session.session_key}/{file_name}"
            TemporaryDocumentStorage().delete(object_key)
            if is_ajax(self.request):
                return JsonResponse({"success": True}, status=200)
            else:
                return redirect(reverse("upload_documents"))

        if is_ajax(self.request):
            return JsonResponse({"success": False}, status=400)
        else:
            return redirect(reverse("upload_documents"))


class DownloadDocumentView(View):
    http_method_names = ["get"]

    def get(self, *args: object, file_name, **kwargs: object) -> HttpResponse:
        user_uploaded_files = get_user_uploaded_files(self.request.session)

        if file_name in user_uploaded_files:
            logger.info(f"User is downloading file: {file_name}")
            # the object key is actually prefixed with the session key according to the logic in CustomFileUploadHandler
            file_url = generate_presigned_url(TemporaryDocumentStorage(), f"{self.request.session.session_key}/{file_name}")
            return redirect(file_url)

        raise Http404()
