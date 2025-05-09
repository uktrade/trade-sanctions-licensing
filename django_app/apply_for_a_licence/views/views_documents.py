import logging
from typing import Any

from apply_for_a_licence.choices import StatusChoices
from apply_for_a_licence.forms import forms_documents as forms
from apply_for_a_licence.models import Document
from authentication.mixins import LoginRequiredMixin
from core.utils import is_ajax
from core.views.base_views import BaseSaveAndReturnFormView, BaseSaveAndReturnView
from django.forms import Form
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View

logger = logging.getLogger(__name__)


class UploadDocumentsView(BaseSaveAndReturnFormView):
    """View for uploading documents.
    Accepts both Ajax and non-Ajax requests, to accommodate both JS and non-JS users respectively."""

    form_class = forms.UploadDocumentsForm
    template_name = "apply_for_a_licence/form_steps/upload_documents.html"

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        """Retrieve the already uploaded files from the session storage and add them to the context."""
        context = super().get_context_data(**kwargs)
        context["uploaded_files"] = self.licence_object.documents.all()
        return context

    def form_valid(self, form: forms.UploadDocumentsForm) -> HttpResponse:
        """Loop through the files and save them to the temporary storage. If the request is Ajax, return a JsonResponse.

        If the request is not Ajax, redirect to the summary page (the next step in the form)."""

        if form.cleaned_data["file"]:
            for file in form.cleaned_data["file"]:
                document = Document(
                    licence=self.licence_object,
                    temp_file=file,
                    original_file_name=file.original_name,
                )
                document.save()

                if is_ajax(self.request):
                    # if it's an AJAX request, then files are sent to this view one at a time, so we can return a response
                    # immediately, and not at the end of the for-loop
                    return JsonResponse(
                        {
                            "success": True,
                            "file_name": document.original_file_name,
                            "s3_key": document.s3_key,
                        },
                        status=201,
                    )
        return super().form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        if is_ajax(self.request):
            return JsonResponse(
                {
                    "success": False,
                    "error": form.errors["file"][0],
                    "file_name": form.files["file"].original_name,
                },
                status=200,
            )
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        success_url = reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class DeleteDocumentsView(LoginRequiredMixin, View):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        if s3_key_to_delete := self.request.POST.get("s3_key_to_delete"):
            document_object = get_object_or_404(Document, temp_file=s3_key_to_delete)
            licence_object = document_object.licence
            if licence_object.user != self.request.user:
                raise Http404()

            if licence_object.status != StatusChoices.draft:
                raise Http404()

            document_object.delete()
            if is_ajax(self.request):
                return JsonResponse({"success": True}, status=200)
            else:
                return redirect(reverse("upload_documents", kwargs={"licence_pk": self.kwargs["licence_pk"]}))
        else:
            raise Http404()


class DownloadDocumentView(BaseSaveAndReturnView):
    http_method_names = ["get"]

    def get(self, *args: object, **kwargs: object) -> HttpResponse:
        document_object = get_object_or_404(Document, pk=self.kwargs["pk"])
        licence_object = document_object.licence
        if licence_object.user != self.request.user:
            raise Http404()

        if licence_object != self.licence_object:
            raise Http404()

        # the object key is actually prefixed with the session key according to the logic in CustomFileUploadHandler
        file_url = document_object.url
        logger.info(
            f"User {self.request.user.email} has downloaded file: {document_object.original_file_name} (PK {document_object.pk})"
        )
        return redirect(file_url)
