from typing import Any

from core.forms.base_forms import BaseForm
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect


class AddAnEntityView(BaseFormView):
    """Base view for adding an entity to a session variable. This is used for infinitely looping sub-journeys, such as
    add a business/recipient/individual."""

    template_name = "core/base_form_step.html"

    def setup(self, request, *args, **kwargs):
        self.retrieved_from_session = False
        return super().setup(request, *args, **kwargs)

    @property
    def session_key(self) -> str:
        """The key in the session where the entities are stored. This should be unique to the view.

        e.g. "businesses", "recipients", "individuals" etc."""
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def url_parameter_key(self) -> str:
        """The key in the URL where the entity UUID is stored.

        e.g. "business_uuid", "recipient_uuid", "individual_uuid" etc."""
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def redirect_after_post(self) -> bool:
        if self.request.GET.get("change") == "yes":
            # if we are creating a new one, then we want to take them to the next step
            return False
        else:
            return True

    def get_form_kwargs(self) -> dict[str, Any]:
        """We want to prefil the form with data already stored in the session if it exists."""
        kwargs = super().get_form_kwargs()

        if self.request.method == "GET":
            # restore the form data from the session, if it exists
            if existing_uuid := str(self.kwargs[self.url_parameter_key]):
                if existing_dict := self.request.session.get(self.session_key, {}).get(existing_uuid, None):
                    kwargs["data"] = self.get_session_data(existing_dict)
                    self.retrieved_from_session = True

        return kwargs

    def get_form(self, form_class=None):
        """If we have retrieved the form from the session, we want to bind it with the data.

        This basically overrides any ?change or ?update query parameters that are passed in the URL."""
        form = super().get_form(form_class)
        if self.request.method == "GET" and self.retrieved_from_session:
            form.is_bound = True
        return form

    def form_valid(self, form: BaseForm) -> HttpResponse:
        """Saving the form data to the session."""
        current_entities = self.request.session.get(self.session_key, {})
        entity_uuid = str(self.kwargs[self.url_parameter_key])

        if entity_uuid not in current_entities:
            current_entities[entity_uuid] = {}

        current_entities[entity_uuid].update(self.set_session_data(form))

        self.entity_uuid = entity_uuid
        self.request.session[self.session_key] = current_entities

        return super().form_valid(form)

    def set_session_data(self, form: BaseForm) -> dict[str, Any]:
        """Override this method to return the data you want to store in the session."""
        return {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }

    def get_session_data(self, session_data: dict[str, Any]) -> dict[str, Any]:
        """Override this method to return the data you want to prefill the form with"""
        return session_data["dirty_data"]


class DeleteAnEntityView(BaseFormView):
    """Base view for deleting an entity from a session variable. This is used for infinitely looping sub-journeys, such as
    add a business/recipient/individual."""

    allow_zero_entities = False

    @property
    def session_key(self) -> str:
        """The key in the session where the entities are stored. This should be unique to the view.

        e.g. "businesses", "recipients", "individuals" etc."""
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def url_parameter_key(self) -> str:
        """The key in the URL where the entity UUID is stored.

        e.g. "business_uuid", "recipient_uuid", "individual_uuid" etc."""
        raise NotImplementedError("You must implement this property in your subclass")

    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        """Remove the entity from the session and redirect back to the success URL."""
        entities = self.request.session.get(self.session_key, [])
        # at least one entity must be added
        if self.allow_zero_entities or len(entities) > 1:
            if entity_uuid := self.request.POST.get(self.url_parameter_key):
                entities.pop(entity_uuid, None)
                self.request.session[self.session_key] = entities

        return redirect(self.get_success_url())
