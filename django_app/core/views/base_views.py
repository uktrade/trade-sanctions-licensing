from django.http import HttpRequest, HttpResponse
from django.views.generic import FormView
from django_ratelimit.exceptions import Ratelimited


class BaseFormView(FormView):
    template_name = "core/base_form_step.html"

    def form_valid(self, form):
        # we want to assign the form to the view ,so we can access it in the get_success_url method
        self.form = form

        # we want to store the form data in the session, so we can access it later on
        self.request.session[self.__class__.__name__] = form.data
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update({"request": self.request})
        # restore the form data from the session, if it exists
        if self.request.method == "GET":
            kwargs["data"] = self.request.session.get(self.__class__.__name__, None)
        return kwargs


def rate_limited_view(request: HttpRequest, exception: Ratelimited) -> HttpResponse:
    return HttpResponse("You have made too many", status=429)
