import logging

from apply_for_a_licence.forms import forms_existing_licence as forms
from core.views.base_views import BaseFormView
from django.urls import reverse

logger = logging.getLogger(__name__)


class PreviousLicenceView(BaseFormView):
    form_class = forms.ExistingLicencesForm

    def get_success_url(self):
        success_url = reverse("type_of_service")
        if start_view := self.request.session.get("start", False):
            if start_view.get("who_do_you_want_the_licence_to_cover") == "individual":
                success_url = reverse("business_employing_individual")
        return success_url
