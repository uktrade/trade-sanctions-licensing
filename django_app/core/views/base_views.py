import datetime
import re
from typing import Any

from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import can_user_edit_licence
from authentication.mixins import LoginRequiredMixin
from core.forms.base_forms import BaseForm, BaseModelForm
from django.conf import settings
from django.forms import Form
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView, FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from playwright.sync_api import PdfMargins, sync_playwright


class BaseView(LoginRequiredMixin, View):
    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseBase:
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(reverse("authentication:logout"))

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()
        return super().dispatch(request, *args, **kwargs)


class BaseTemplateView(BaseView, TemplateView):
    pass


class BaseSaveAndReturnView(BaseView):
    @property
    def licence_object(self) -> Licence | None:
        if licence_id := self.kwargs.get("licence_pk", None):
            try:
                licence = Licence.objects.get(pk=licence_id)
                if not can_user_edit_licence(self.request.user, licence):
                    raise Http404()
                else:
                    self._licence_object = licence
                    return licence
            except Licence.DoesNotExist:
                return None
        else:
            return None


class BaseSaveAndReturnFormView(BaseSaveAndReturnView, FormView):
    template_name = "core/base_form_step.html"
    # do we want to redirect the user to the redirect_to query parameter page after this form is submitted?
    redirect_after_post = True

    # do we want to redirect the user to the next step with query parameters?
    redirect_with_query_parameters = False

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if self.request.GET.get("update", None) == "yes":
            self.update = True
        else:
            self.update = False

        return super().dispatch(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponse:
        if self.request.POST.get("skip_link"):
            return HttpResponseRedirect(reverse("tasklist", kwargs={"licence_pk": self.licence_object.id}))
        else:
            return super().post(request, *args, **kwargs)

    def get_form(self, form_class: BaseForm | None = None) -> BaseForm:
        form = super().get_form(form_class)
        self.form = form
        return form

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form: Form) -> HttpResponse:
        return HttpResponseRedirect(self.get_next_url())

    def get_next_url(self) -> str:
        """Get the URL of the next page, could either be the next step, tasklist, or a redirect_to.

        We abstract this to another method so that views can call it without having to use/re-use form_valid"""
        # figure out if we want to redirect after form is submitted
        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return reverse(redirect_to_url, kwargs={"licence_pk": self.licence_object.id})
            else:
                # we don't want to redirect the user just now, but we want to pass the redirect_to URL to the next form,
                # so it can redirect the user after it is submitted
                self.request.session["redirect_to_url"] = redirect_to_url

        success_url = self.get_success_url()
        if self.redirect_with_query_parameters:
            success_url = self.add_query_parameters_to_url(success_url)

        return success_url

    def add_query_parameters_to_url(self, success_url: str) -> str:
        """Add GET query parameters to the success URL so they're retained."""
        if get_parameters := self.request.GET.urlencode():
            updated_parameters = re.sub(r"(business|yourself|individual|recipient)_id=\d+&?", "", get_parameters)
            if updated_parameters:
                success_url += "?" + updated_parameters
        return success_url

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if licence := self.licence_object:
            context["licence"] = licence
        return context


class BaseSaveAndReturnModelFormView(SingleObjectMixin, BaseSaveAndReturnFormView):
    def get_form(self, form_class=None) -> BaseModelForm:
        form = super().get_form(form_class)
        self.form: BaseModelForm = form
        return form

    def form_valid(self, form: Form) -> HttpResponse:
        self.instance = self.save_form(form)
        return super().form_valid(form)

    def save_form(self, form: Form) -> Form:
        return form.save()


class BaseSaveAndReturnLicenceModelFormView(BaseSaveAndReturnModelFormView):
    @property
    def object(self):
        return self.licence_object

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs


class BaseDownloadPDFView(DetailView):
    template_name = "core/base_download_pdf.html"
    header = "Apply for a licence to provide sanctioned trade services"

    def get(self, request: HttpRequest, **kwargs: object) -> HttpResponse:
        self.reference = self.request.GET.get("reference", "")
        filename = f"application-{self.reference}.pdf"
        pdf_data = None
        template_string = render_to_string(self.template_name, context=self.get_context_data(**kwargs))
        margins = PdfMargins(left="1.25in", right="1.25in", top="1in", bottom="1in")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(mark_safe(template_string))
            page.wait_for_function("document.fonts.ready.then(fonts => fonts.status === 'loaded')")
            pdf_data = page.pdf(format="A4", tagged=True, margin=margins)
            browser.close()

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f"inline; filename={filename}"
        return response

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        self.object: list[Any] = []
        context = super().get_context_data(**kwargs)
        context["header"] = self.header
        context["reference"] = self.reference
        return context
