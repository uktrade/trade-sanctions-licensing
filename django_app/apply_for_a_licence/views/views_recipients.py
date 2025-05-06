import logging
from typing import Type

from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.forms import forms_recipients as forms
from apply_for_a_licence.models import Organisation
from apply_for_a_licence.views.base_views import AddAnEntityView, DeleteAnEntityView
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class BaseRecipientFormView(AddAnEntityView):
    pk_url_kwarg = "recipient_id"
    model = Organisation
    context_object_name = "recipient"


class WhereIsTheRecipientLocatedView(BaseRecipientFormView):
    form_class = forms.WhereIsTheRecipientLocatedForm
    redirect_after_post = False
    redirect_with_query_parameters = True

    def get_recipient_id(self):
        if self.request.GET.get("new", ""):
            # The user wants to add a new recipient, create it now and assign the id
            # Lookup first to make sure there are no ghost ids
            new_recipient, created = Organisation.objects.get_or_create(
                licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.recipient, status="draft"
            )
            return new_recipient.id
        else:
            recipient_id = self.request.GET.get("recipient_id") or self.kwargs[self.pk_url_kwarg]
            if recipient_id:
                return int(recipient_id)
        return None

    def dispatch(self, request, *args, **kwargs):
        if recipient_id := self.get_recipient_id():
            self.kwargs[self.pk_url_kwarg] = recipient_id
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.has_field_changed("where_is_the_address"):
            # if the field has changed, we need to clear the recipient address data and set the status to draft
            form.instance.clear_address_data()
            form.instance.where_is_the_address = form.cleaned_data["where_is_the_address"]
            form.instance.status = "draft"
            form.instance.save()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        location = self.form.cleaned_data["where_is_the_address"]
        success_url = reverse(
            "add_a_recipient",
            kwargs={
                "licence_pk": self.kwargs["licence_pk"],
                "location": location,
                "recipient_id": self.kwargs[self.pk_url_kwarg],
            },
        )
        return success_url


class AddARecipientView(BaseRecipientFormView):
    redirect_after_post = False

    def setup(self, request, *args, **kwargs):
        self.location = kwargs["location"]
        return super().setup(request, *args, **kwargs)

    def get_form_class(self) -> Type[forms.AddAUKRecipientForm | forms.AddANonUKRecipientForm]:
        if self.kwargs["location"] == "in-uk":
            form_class = forms.AddAUKRecipientForm
        else:
            form_class = forms.AddANonUKRecipientForm
        return form_class

    def get_success_url(self):
        success_url = reverse(
            "relationship_provider_recipient",
            kwargs={"licence_pk": self.kwargs["licence_pk"], "recipient_id": self.kwargs[self.pk_url_kwarg]},
        )
        return success_url


class RecipientAddedView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.RecipientAddedForm
    template_name = "apply_for_a_licence/form_steps/recipient_added.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["licence_object"] = self.licence_object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recipients"] = Organisation.objects.filter(
            licence=self.licence_object, type_of_relationship=TypeOfRelationshipChoices.recipient.value
        )
        return context

    def get_success_url(self) -> str:
        add_recipient = self.form.cleaned_data["do_you_want_to_add_another_recipient"]
        if add_recipient:
            new_recipient = Organisation.objects.create(
                licence=self.licence_object,
                type_of_relationship=TypeOfRelationshipChoices.recipient,
            )
            success_url = (
                reverse("where_is_the_recipient_located", kwargs={"licence_pk": self.kwargs["licence_pk"]})
                + f"?recipient_id={new_recipient.id}"
            )
        else:
            success_url = reverse("tasklist", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class DeleteRecipientView(DeleteAnEntityView):
    model = Organisation
    pk_url_kwarg = "recipient_id"
    allow_zero_entities = True

    def get_success_url(self):
        success_url = reverse("recipient_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url


class RelationshipProviderRecipientView(BaseRecipientFormView):
    form_class = forms.RelationshipProviderRecipientForm
    redirect_with_query_parameters = False  # once we're done here, we don't care about the query parameters

    def save_form(self, form):
        instance = form.save(commit=False)
        instance.status = choices.EntityStatusChoices.complete
        instance.save()
        return instance

    def get_success_url(self):
        success_url = reverse("recipient_added", kwargs={"licence_pk": self.kwargs["licence_pk"]})
        return success_url
