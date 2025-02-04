import logging
import uuid
from typing import Type

from apply_for_a_licence.choices import TypeOfRelationshipChoices, TypeOfServicesChoices
from apply_for_a_licence.forms import forms_recipients as forms
from apply_for_a_licence.models import Organisation
from apply_for_a_licence.views.base_views import DeleteAnEntityView
from core.views.base_views import BaseFormView, BaseRecipientFormView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class WhereIsTheRecipientLocatedView(BaseRecipientFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm
    redirect_after_post = False

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get("recipient_uuid", ""):
            if not Organisation.objects.filter(pk=self.kwargs["recipient_uuid"]).exists():
                # let's create a new recipient if it doesn't exist
                licence_object = self.get_current_licence_object()
                Organisation.objects.create(
                    pk=self.kwargs["recipient_uuid"],
                    licence=licence_object,
                    type_of_relationship=TypeOfRelationshipChoices.recipient.value,
                )

            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}))

    def form_valid(self, form):
        if form.has_field_changed("where_is_the_address"):
            # if the field has changed, we need to clear the recipient address data
            form.instance.clear_address_data()
            form.instance.where_is_the_address = form.cleaned_data["where_is_the_address"]
        return super().form_valid(form)

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse("add_a_recipient", kwargs={"location": location, "recipient_uuid": self.kwargs["recipient_uuid"]})
        return success_url


class AddARecipientView(BaseRecipientFormView):
    def get_form_class(self) -> Type[forms.AddAUKRecipientForm | forms.AddANonUKRecipientForm]:
        if self.kwargs["location"] == "in-uk":
            form_class = forms.AddAUKRecipientForm
        else:
            form_class = forms.AddANonUKRecipientForm
        return form_class

    def get_success_url(self):
        success_url = reverse("relationship_provider_recipient", kwargs={"recipient_uuid": self.form.instance.pk})
        return success_url


class RecipientAddedView(BaseFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        licence = self.get_current_licence_object()
        context["recipients"] = licence.organisations.filter(type_of_relationship=TypeOfRelationshipChoices.recipient.value)
        return context

    def get_success_url(self) -> str:
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            success_url = reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}) + "?new=yes"
        else:
            licence = self.get_current_licence_object()
            if licence.type_of_service == TypeOfServicesChoices.professional_and_business.value:
                success_url = reverse("licensing_grounds")
            else:
                success_url = reverse("purpose_of_provision")

        return success_url


class DeleteRecipientView(DeleteAnEntityView):
    success_url = reverse_lazy("recipient_added")
    session_key = "recipients"
    url_parameter_key = "recipient_uuid"


class RelationshipProviderRecipientView(BaseRecipientFormView):
    form_class = forms.RelationshipProviderRecipientForm
    success_url = reverse_lazy("recipient_added")
