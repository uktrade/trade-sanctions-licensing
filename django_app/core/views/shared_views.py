import os
from typing import Any

from django.conf import settings
from django.http import FileResponse, HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from playwright.sync_api import sync_playwright


class DownloadPDFView(TemplateView):
    template_name = "core/application_pdf.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> FileResponse:
        context_data = self.get_context_data()
        self.filename = f"application-{context_data['reference']}.pdf"
        template_string = render_to_string(self.template_name, context=context_data)
        pdf_path = os.path.join(settings.BASE_DIR, self.filename)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            page.pdf(format="A4", path=pdf_path)
            browser.close()

        return FileResponse(open(pdf_path, "rb"), filename=self.filename, as_attachment=True)

    def get_context_data(self, *args: object, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["reference"] = self.request.GET.get("reference")
        return context
