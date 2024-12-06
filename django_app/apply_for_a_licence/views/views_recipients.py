import logging
import urllib.parse
import uuid

from apply_for_a_licence.choices import TypeOfServicesChoices
from apply_for_a_licence.forms import forms_recipients as forms
from apply_for_a_licence.utils import get_cleaned_data_for_step
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class WhereIsTheRecipientLocatedView(BaseFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm
    redirect_after_post = False

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get("recipient_uuid", ""):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}))

    def form_valid(self, form: forms.WhereIsTheRecipientLocatedForm) -> HttpResponse:
        recipient_uuid = str(self.kwargs["recipient_uuid"])

        # first time a recipient is created
        if not self.request.session.get("recipient_locations", ""):
            self.request.session["recipient_locations"] = {
                recipient_uuid: {"location": form.cleaned_data["where_is_the_address"], "changed": False}
            }
            return super().form_valid(form)

        # new recipient is added
        if recipient_uuid not in self.request.session["recipient_locations"].keys():
            self.request.session["recipient_locations"][recipient_uuid] = {
                "location": form.cleaned_data["where_is_the_address"],
                "changed": False,
            }
            return super().form_valid(form)

        # recipient data is changing
        if self.request.GET.get("change"):
            recipient_data = self.request.session["recipient_locations"][recipient_uuid]
            past_choice = recipient_data["location"]
            if past_choice != form.cleaned_data["where_is_the_address"]:
                recipient_data["changed"] = True
                # update the location in case the user selects change again
                recipient_data["location"] = form.cleaned_data["where_is_the_address"]

        return super().form_valid(form)

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse("add_a_recipient", kwargs={"location": location, "recipient_uuid": self.kwargs["recipient_uuid"]})
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url


class AddARecipientView(AddAnEntityView):
    session_key = "recipients"
    url_parameter_key = "recipient_uuid"

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        recipient_uuid = str(self.kwargs["recipient_uuid"])

        if self.request.method == "GET" and self.request.GET.get("change", ""):
            if recipients := self.request.session.get("recipient_locations", {}):

                # recipient location has changed, clear the form
                if recipients.get(recipient_uuid, {}).get("changed", ""):
                    form.is_bound = False

                    # delete the recipients session data so we don't have conflicts before the save
                    if self.request.session.get("recipients", {}).get(recipient_uuid, ""):
                        del self.request.session["recipients"][recipient_uuid]

                # recipient has not changed location choice
                else:
                    form.is_bound = True

        # the user submitted the form, update "changed" in order to wipe the slate
        elif self.request.method == "POST":
            if recipients := self.request.session.get("recipient_locations", {}):
                if recipients.get(recipient_uuid, {}):
                    recipients[recipient_uuid]["changed"] = False

        return form

    def get_form_class(self) -> forms.AddAUKRecipientForm | forms.AddANonUKRecipientForm:
        if self.location == "in-uk":
            form_class = forms.AddAUKRecipientForm
        else:
            form_class = forms.AddANonUKRecipientForm
        return form_class

    def get_success_url(self):
        success_url = reverse("relationship_provider_recipient", kwargs={"recipient_uuid": self.entity_uuid})
        if get_parameters := urllib.parse.urlencode(self.request.GET):
            success_url += "?" + get_parameters

        return success_url


class RecipientAddedView(BaseFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_success_url(self):
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            return reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}) + "?change=yes"
        else:
            type_of_service_data = get_cleaned_data_for_step(self.request, "type_of_service")
            if type_of_service_data.get("type_of_service") == TypeOfServicesChoices.professional_and_business.value:
                return reverse("licensing_grounds")
            else:
                return reverse("purpose_of_provision")


class DeleteRecipientView(DeleteAnEntityView):
    success_url = reverse_lazy("recipient_added")
    session_key = "recipients"
    url_parameter_key = "recipient_uuid"


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
        # pre-filling the correct relationship for this recipient if it's a GET
        if self.request.method == "GET":
            if relationship := self.request.session.get("recipients", {}).get(recipient_uuid, {}).get("relationship"):
                kwargs["data"] = {"relationship": relationship}
                self.existing_relationship = True
            else:
                self.existing_relationship = False
        return kwargs

    def get_form(self, form_class=None):
        """We want to pre-fill the form only if the relationship has been already set."""
        form = super().get_form(form_class)
        if self.request.method == "GET":
            if self.existing_relationship:
                form.is_bound = True
            else:
                form.is_bound = False
        return form
