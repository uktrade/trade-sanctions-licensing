from django.urls import reverse

from apply_for_a_licence.utils import get_dirty_form_data
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import FormView, RedirectView
from django_ratelimit.exceptions import Ratelimited

from core.sites import is_apply_for_a_licence_site, is_view_a_licence_site


class BaseFormView(FormView):
    template_name = "core/base_form_step.html"

    # do we want to redirect the user to the redirect_to query parameter page after this form is submitted?
    redirect_after_post = True

    @property
    def step_name(self) -> str:
        """Get the step name from the view class name."""
        from apply_for_a_licence.urls import view_to_step_dict

        step_name = view_to_step_dict[self.__class__.__name__]

        return step_name

    def form_valid(self, form):
        # we want to assign the form to the view ,so we can access it in the get_success_url method
        self.form = form
        # we want to store the dirty form data in the session, so we can access it later on
        form_data = dict(form.data.copy())

        # first get rid of some useless cruft
        form_data.pop("csrfmiddlewaretoken", None)
        form_data.pop("encoding", None)

        # Django QueryDict is a weird beast, we need to check if the key maps to a list of values (as it does with a
        # multi-select field) and if it does, we need to convert it to a list. If not, we can just keep the value as is.
        for key, value in form_data.items():
            if len(value) == 1:
                form_data[key] = value[0]

        # now keep it in the session
        self.request.session[self.step_name] = form_data
        redirect_to_url = self.request.GET.get("redirect_to_url", None) or self.request.session.pop("redirect_to_url", None)
        if redirect_to_url and url_has_allowed_host_and_scheme(redirect_to_url, allowed_hosts=None):
            if self.redirect_after_post:
                # we want to redirect the user to a specific page after the form is submitted
                return redirect(redirect_to_url)
            else:
                # we don't want to redirect the user just now, but we want to pass the redirect_to URL to the next form,
                # so it can redirect the user after it is submitted
                self.request.session["redirect_to_url"] = redirect_to_url

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["request"] = self.request

        # restore the form data from the session, if it exists
        if self.request.method == "GET":
            if previous_data := get_dirty_form_data(self.request, self.step_name):
                kwargs["data"] = previous_data
        return kwargs


def rate_limited_view(request: HttpRequest, exception: Ratelimited) -> HttpResponse:
    return HttpResponse("You have made too many", status=429)


class RedirectBaseDomainView(RedirectView):
    """Redirects base url visits to either report a breach app or view app default view"""

    @property
    def url(self) -> str:
        if is_apply_for_a_licence_site(self.request.site):
            return reverse("start")
        elif is_view_a_licence_site(self.request.site):
            # if users are not accessing a specific page in view-a-suspected-breach - raise a 404
            # unless they are staff, in which case take them to the manage users page
            if self.request.user.is_staff:
                return reverse("view_a_suspected_breach:user_admin")
            else:
                raise Http404()
        return ""

