import datetime

from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import can_user_edit_licence
from authentication.mixins import LoginRequiredMixin
from core.forms.base_forms import BaseForm, BaseModelForm
from django.conf import settings
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin


class BaseView(LoginRequiredMixin, View):

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseBase:
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(
                    reverse("authentication:logout", kwargs={"token": self.request.session["_one_login_token"]["id_token"]})
                )

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()
        return super().dispatch(request, *args, **kwargs)


class BaseTemplateView(BaseView, TemplateView):
    pass


class BaseSaveAndReturnView(BaseView):
    @property
    def licence_object(self) -> Licence | None:
        if licence_id := self.request.session.get("licence_id"):
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

    def dispatch(self, request: HttpRequest, *args: object, **kwargs: object) -> HttpResponseRedirect | HttpResponseBase:
        # checking for session expiry
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(reverse("authentication:logout"))

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["id_token"] = self.request.session["_one_login_token"]["id_token"]
        return context


class BaseSaveAndReturnFormView(BaseSaveAndReturnView, FormView):
    template_name = "core/base_form_step.html"
    # do we want to redirect the user to the redirect_to query parameter page after this form is submitted?
    redirect_after_post = True

    # do we want to redirect the user to the next step with query parameters?
    redirect_with_query_parameters = False

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if self.request.GET.get("update", None) == "yes":
            self.update = True
        else:
            self.update = False

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get("skip_link"):
            return HttpResponseRedirect(reverse("tasklist"))
        else:
            return super().post(request, *args, **kwargs)

    def get_form(self, form_class: BaseForm | None = None) -> BaseForm:
        form = super().get_form(form_class)
        self.form = form
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_next_url())

    def get_next_url(self) -> str:
        """Get the URL of the next page, could either be the next step, tasklist, or a redirect_to.

        We abstract this to another method so that views can call it without having to use/re-use form_valid"""
        # figure out if we want to redirect after form is submitted
        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return reverse(redirect_to_url)
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
            success_url += "?" + get_parameters
        return success_url


class BaseSaveAndReturnModelFormView(SingleObjectMixin, BaseSaveAndReturnFormView):
    def get_form(self, form_class=None) -> BaseModelForm:
        form = super().get_form(form_class)
        self.form: BaseModelForm = form
        return form

    def form_valid(self, form):
        self.instance = self.save_form(form)
        return super().form_valid(form)

    def save_form(self, form):
        return form.save()


class BaseSaveAndReturnLicenceModelFormView(BaseSaveAndReturnModelFormView):
    @property
    def object(self):
        return self.licence_object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs
