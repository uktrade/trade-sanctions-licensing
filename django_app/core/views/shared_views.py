from typing import Any

from django.http import HttpRequest, HttpResponse

# from django.template.loader import render_to_string
# from playwright.sync_api import sync_playwright
from wkhtmltopdf.views import PDFTemplateView


class DownloadPDFView(PDFTemplateView):
    template_name = "apply_for_a_licence/test_for_pdf.html"

    def get(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        reference = self.request.GET.get("reference")
        self.filename = f"application-{reference}.pdf"
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args: object, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context["reference"] = self.request.GET.get("reference")
        return context


class PWDownloadPDFView:
    pass
