import logging
import urllib.parse
import uuid

from apply_for_a_licence.forms import forms_recipients as forms
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class WhereIsTheRecipientLocatedView(BaseFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm
    redirect_after_post = False

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        return reverse("add_a_recipient", kwargs={"location": location}) + "?" + urllib.parse.urlencode(self.request.GET)


class AddARecipientView(BaseFormView):
    form_class = forms.AddARecipientForm
    template_name = "core/base_form_step.html"
    redirect_after_post = False

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        # restore the form data from the recipient_uuid, if it exists
        if self.request.method == "GET":
            if recipient_uuid := self.request.GET.get("recipient_uuid", None):
                if recipient_dict := self.request.session.get("recipients", {}).get(recipient_uuid, None):
                    kwargs["data"] = recipient_dict["dirty_data"]
        if self.location == "in_the_uk":
            kwargs["is_uk_address"] = True
        return kwargs

    def form_valid(self, form: forms.AddARecipientForm) -> HttpResponse:
        current_recipients = self.request.session.get("recipients", {})
        # get the recipient_uuid if it exists, otherwise create it
        if recipient_uuid := self.request.GET.get("recipient_uuid", self.kwargs.get("recipient_uuid", str(uuid.uuid4()))):
            # used to display the recipient_uuid data in recipient_added.html
            self.recipient_uuid = recipient_uuid

            if recipient_uuid not in current_recipients:
                current_recipients[recipient_uuid] = {}

            current_recipients[recipient_uuid].update(
                {
                    "cleaned_data": form.cleaned_data,
                    "dirty_data": form.data,
                }
            )
        self.request.session["recipients"] = current_recipients

        return super().form_valid(form)

    def get_success_url(self):
        return (
            reverse("relationship_provider_recipient", kwargs={"recipient_uuid": self.recipient_uuid})
            + "?"
            + urllib.parse.urlencode(self.request.GET)
        )


class RecipientAddedView(BaseFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_success_url(self):
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            return reverse("where_is_the_recipient_located") + "?change=yes"
        else:
            return reverse("licensing_grounds")


class DeleteRecipientView(BaseFormView):
    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        recipients = self.request.session.get("recipients", [])
        # at least one recipient must be added
        if len(recipients) > 1:
            if recipients_uuid := self.request.POST.get("recipient_uuid"):
                recipients.pop(recipients_uuid, None)
                self.request.session["recipients"] = recipients
        return redirect(reverse_lazy("recipient_added"))


class RelationshipProviderRecipientView(BaseFormView):
    form_class = forms.RelationshipProviderRecipientForm
    success_url = reverse_lazy("recipient_added")

    def form_valid(self, form):
        """Setting the relationship between the provider and this particular recipient."""
        recipient_uuid = self.kwargs["recipient_uuid"]
        recipients = self.request.session.get("recipients", {})
        recipients[recipient_uuid]["relationship"] = form.cleaned_data["relationship"]
        self.request.session["recipients"] = recipients
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        recipient_uuid = self.kwargs["recipient_uuid"]
        # pre-filling the correct relationship for this recipient
        if relationship := self.request.session.get("recipients", {}).get(recipient_uuid, None).get("relationship"):
            kwargs["data"] = {"relationship": relationship}
            self.existing_relationship = True
        else:
            self.existing_relationship = False
        return kwargs

    def get_form(self, form_class=None):
        """We want to pre-fill the form only if the relationship has been already set."""
        form = super().get_form(form_class)
        if self.request.method == "GET" and not self.existing_relationship:
            form.is_bound = False
        return form
