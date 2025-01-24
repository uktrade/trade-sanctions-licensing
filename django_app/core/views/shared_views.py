from typing import Any

from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from playwright.sync_api import sync_playwright


class DownloadPDFView(TemplateView):
    # TODO: update the template when DST-798 is complete
    # todo - only show licence applications that belong to the requesting user
    template_name = "core/application_pdf.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        context_data = self.get_context_data()
        filename = f"application-{context_data['reference']}.pdf"
        pdf_data = None
        template_string = render_to_string(self.template_name, context=context_data)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            pdf_data = page.pdf(format="A4")
            browser.close()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={filename}"

        return response

    def get_context_data(self, *args: object, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["reference"] = self.request.GET.get("reference", "")
        return context
