import logging
import uuid
from typing import Type

from apply_for_a_licence.choices import TypeOfRelationshipChoices, TypeOfServicesChoices
from apply_for_a_licence.forms import forms_recipients as forms
from apply_for_a_licence.models import Organisation
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseSaveAndReturnFormView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

logger = logging.getLogger(__name__)


class BaseRecipientFormView(AddAnEntityView):
    pk_url_kwarg = "recipient_uuid"
    model = Organisation
    context_object_name = "recipient"


class WhereIsTheRecipientLocatedView(BaseRecipientFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm
    redirect_after_post = False

    @property
    def object(self) -> Organisation:
        # let's create a new recipient if it doesn't exist
        instance, _ = Organisation.objects.get_or_create(
            pk=self.kwargs[self.pk_url_kwarg],
            defaults={
                "licence": self.licence_object,
                "type_of_relationship": TypeOfRelationshipChoices.recipient.value,
            },
        )
        return instance

    def dispatch(self, request, *args, **kwargs):
        if not self.kwargs.get(self.pk_url_kwarg, ""):
            # if they've entered here via CYA 'add new recipient', we need to come up with one
            return redirect(reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.has_field_changed("where_is_the_address"):
            # if the field has changed, we need to clear the recipient address data
            form.instance.clear_address_data()
            form.instance.where_is_the_address = form.cleaned_data["where_is_the_address"]
            form.instance.save()
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


class RecipientAddedView(BaseSaveAndReturnFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipients"] = Organisation.objects.filter(
            licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.recipient.value
        )
        return context

    def get_success_url(self) -> str:
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            success_url = reverse("where_is_the_recipient_located", kwargs={"recipient_uuid": uuid.uuid4()}) + "?new=yes"
        else:
            if self.licence_object.type_of_service == TypeOfServicesChoices.professional_and_business.value:
                success_url = reverse("licensing_grounds")
            else:
                success_url = reverse("purpose_of_provision")

        return success_url


class DeleteRecipientView(DeleteAnEntityView):
    success_url = reverse_lazy("recipient_added")
    model = Organisation
    pk_url_kwarg = "recipient_uuid"
    allow_zero_entities = True


class RelationshipProviderRecipientView(BaseRecipientFormView):
    form_class = forms.RelationshipProviderRecipientForm
    success_url = reverse_lazy("recipient_added")
    redirect_with_query_parameters = False  # once we're done here, we don't care about the query parameters
