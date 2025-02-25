import logging
from typing import Any

from apply_for_a_licence.forms import forms_existing_licence as forms
from core.views.base_views import BaseSaveAndReturnLicenceModelFormView
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class PreviousLicenceView(BaseSaveAndReturnLicenceModelFormView):
    form_class = forms.ExistingLicencesForm
    template_name = "apply_for_a_licence/form_steps/conditional_radios_form.html"
    success_url = reverse_lazy("tasklist")

    def get_context_data(self, **kwargs: object) -> dict[str, Any]:
        context = super().get_context_data()
        context["page_title"] = (
            "Have any of the businesses you've added held a licence before to provide "
            "any sanctioned services or export any sanctioned goods?"
        )
        return context
