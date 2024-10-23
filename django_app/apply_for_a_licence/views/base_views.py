from typing import Any

from core.forms.base_forms import BaseForm
from core.views.base_views import BaseFormView
from django.http import HttpResponse
from django.shortcuts import redirect


class AddAnEntityView(BaseFormView):
    template_name = "core/base_form_step.html"

    def setup(self, request, *args, **kwargs):
        self.retrieved_from_session = False
        return super().setup(request, *args, **kwargs)

    @property
    def session_key(self) -> str:
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def url_parameter_key(self) -> str:
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def redirect_after_post(self) -> bool:
        if self.request.GET.get("change") == "yes":
            # if we are creating a new one, then we want to take them to the next step
            return False
        else:
            return True

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()

        if self.request.method == "GET":
            # restore the form data from the session, if it exists
            if existing_uuid := str(self.kwargs[self.url_parameter_key]):
                if existing_dict := self.request.session.get(self.session_key, {}).get(existing_uuid, None):
                    kwargs["data"] = self.get_session_data(existing_dict)
                    self.retrieved_from_session = True

        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == "GET" and self.retrieved_from_session:
            # we always want to bind the form with pre-existing data if we've retrieved it from the session
            form.is_bound = True
        return form

    def form_valid(self, form: BaseForm) -> HttpResponse:
        current_entities = self.request.session.get(self.session_key, {})
        entity_uuid = str(self.kwargs[self.url_parameter_key])

        if entity_uuid not in current_entities:
            current_entities[entity_uuid] = {}

        current_entities[entity_uuid].update(self.set_session_data(form))

        self.entity_uuid = entity_uuid
        self.request.session[self.session_key] = current_entities

        return super().form_valid(form)

    def set_session_data(self, form: BaseForm) -> dict[str, Any]:
        return {
            "cleaned_data": form.cleaned_data,
            "dirty_data": form.data,
        }

    def get_session_data(self, session_data: dict[str, Any]) -> dict[str, Any]:
        return session_data["dirty_data"]


class DeleteAnEntityView(BaseFormView):
    allow_zero_entities = False

    @property
    def session_key(self) -> str:
        raise NotImplementedError("You must implement this property in your subclass")

    @property
    def url_parameter_key(self) -> str:
        raise NotImplementedError("You must implement this property in your subclass")

    def post(self, *args: object, **kwargs: object) -> HttpResponse:
        entities = self.request.session.get(self.session_key, [])
        # at least one entity must be added
        if self.allow_zero_entities or len(entities) > 1:
            if entity_uuid := self.request.POST.get(self.url_parameter_key):
                entities.pop(entity_uuid, None)
                self.request.session[self.session_key] = entities

        return redirect(self.get_success_url())
