import logging
from typing import Any

from apply_for_a_licence.forms import forms_existing_licence as forms
from core.views.base_views import BaseFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class PreviousLicenceView(BaseFormView):
    form_class = forms.ExistingLicencesForm
    template_name = "apply_for_a_licence/form_steps/conditional_radios_form.html"

    def get_success_url(self):
        success_url = reverse("type_of_service")
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                success_url = reverse("business_employing_individual")
        return success_url

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data()
        context["page_title"] = (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )
        return context
