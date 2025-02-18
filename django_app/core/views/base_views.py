import datetime

from apply_for_a_licence.models import Licence
from apply_for_a_licence.utils import get_dirty_form_data
from authentication.mixins import LoginRequiredMixin
from core.forms.base_forms import BaseForm, BaseModelForm
from django import forms
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.detail import SingleObjectMixin


class BaseView(LoginRequiredMixin, View):
    pass


class BaseTemplateView(BaseView, TemplateView):
    pass


class BaseFormView(BaseView, FormView):
    template_name = "core/base_form_step.html"

    # do we want to redirect the user to the redirect_to query parameter page after this form is submitted?
    redirect_after_post = True

    @property
    def step_name(self) -> str:
        """Get the step name from the view class name."""
        from apply_for_a_licence.urls import view_to_step_dict

        step_name = view_to_step_dict[self.__class__.__name__]

        return step_name

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        # restore the form data from the session, if it exists
        if self.request.method == "GET":
            if previous_data := get_dirty_form_data(self.request, self.step_name):
                kwargs["data"] = previous_data
        return kwargs

    def get_form(self, form_class=None):

        form = super().get_form(form_class)
        if self.request.method == "GET" and self.request.GET.get("new"):
            # if we want a new form, we don't want it to be bound
            form.is_bound = False

        return form

    def post(self, request, *args, **kwargs):
        # checking for session expiry
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(reverse("session_expired"))
        else:
            # if we don't have a last activity, we assume the session has expired
            return redirect(reverse("session_expired"))

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()

        return super().post(request, *args, **kwargs)

    def form_valid(self, form: BaseForm):
        # we want to assign the form to the view ,so we can access it in the get_success_url method
        self.form = form

        # we want to store the dirty form data in the session, so we can access it later on
        form_data = dict(form.data.copy())

        # first get rid of some useless cruft
        form_data.pop("csrfmiddlewaretoken", None)
        form_data.pop("encoding", None)

        # Django QueryDict is a weird beast, we need to check if the key maps to a list of values (as it does with a
        # multi-select field) and if it does, we need to convert it to a list. If not, we can just keep the value as is.
        # We also need to keep the value as it is if the form is an ArrayField.
        for key, value in form_data.items():
            if not isinstance(form.fields.get(key), forms.MultipleChoiceField):
                if len(value) == 1:
                    form_data[key] = value[0]

        self.changed_fields = {}
        if previous_data := get_dirty_form_data(self.request, self.step_name):
            for key, value in previous_data.items():
                if key in form_data and form_data[key] != value:
                    self.changed_fields[key] = value

        if self.form.save_and_return:
            self.instance = self.form.save()

        # now keep it in the session
        self.request.session[self.step_name] = form_data

        # get the success_url as this might change the value of redirect_after_post to avoid duplicating conditional
        # logic in the get_success_url method
        success_url = self.get_success_url()

        # figure out if we want to redirect after form is submitted
        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return redirect(redirect_to_url)
            else:
                # we don't want to redirect the user just now, but we want to pass the redirect_to URL to the next form,
                # so it can redirect the user after it is submitted
                self.request.session["redirect_to_url"] = redirect_to_url

        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        # debugging purposes so we can put breakpoints here
        return super().form_invalid(form)


class BaseSaveAndReturnView(BaseView):
    @property
    def licence_object(self) -> Licence | None:
        if licence_id := self.request.session.get("licence_id"):
            try:
                licence = Licence.objects.get(pk=licence_id)
                if licence.user != self.request.user:
                    raise Http404()
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
    redirect_with_query_parameters = True

    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get("update", None) == "yes":
            self.update = True
        else:
            self.update = False

        # checking for session expiry
        if last_activity := request.session.get(settings.SESSION_LAST_ACTIVITY_KEY, None):
            now = timezone.now()
            last_activity = datetime.datetime.fromisoformat(last_activity)
            # if the last recorded activity was more than the session cookie age ago, we assume the session has expired
            if now > (last_activity + datetime.timedelta(seconds=settings.SESSION_COOKIE_AGE)):
                return redirect(reverse("session_expired"))
        else:
            # if we don't have a last activity, we assume the session has expired
            return redirect(reverse("session_expired"))

        # now setting the last active to the current time
        request.session[settings.SESSION_LAST_ACTIVITY_KEY] = timezone.now().isoformat()
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class: BaseForm | None = None) -> BaseForm:
        form = super().get_form(form_class)
        self.form = form
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        # get the success_url as this might change the value of redirect_after_post to avoid duplicating conditional
        # logic in the get_success_url method
        success_url = self.get_success_url()
        if self.redirect_with_query_parameters:
            success_url = self.add_query_parameters_to_url(success_url)

        # figure out if we want to redirect after form is submitted
        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return redirect(redirect_to_url)
            else:
                # we don't want to redirect the user just now, but we want to pass the redirect_to URL to the next form,
                # so it can redirect the user after it is submitted
                self.request.session["redirect_to_url"] = redirect_to_url

        return HttpResponseRedirect(success_url)

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
