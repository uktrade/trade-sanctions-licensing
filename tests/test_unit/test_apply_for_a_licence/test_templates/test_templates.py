from unittest.mock import MagicMock, patch

from crispy_forms_gds.helper import FormHelper
from django.template.loader import get_template

from tests.helpers import get_all_templates_files_for_app


@patch("django.urls.resolvers.URLResolver._reverse_with_prefix")
def test_all_templates_inherit_from_base_logged_in_template(patched_reverse, request_object):
    """Checks all the templates in apply_for_a_licence app inherit from the base_logged_in.html template and
    therefore have the session expiry logic."""
    patched_reverse.return_value = "/"

    app_name = "apply_for_a_licence"

    apply_templates = get_all_templates_files_for_app(app_name)
    for template in apply_templates:
        if "partials" in template.parts or "download_application_pdf" in str(template):
            continue
        else:
            django_template_object = get_template(template)
            context = {
                "request": request_object,
                "form": MagicMock(
                    helper=MagicMock(
                        spec_set=FormHelper, template="apply_for_a_licence/form_steps/partials/uk_nexus_details.html"
                    )
                ),
            }
            rendered = django_template_object.render(context, request_object)
            assert "session_expiry_dialog" in rendered
            assert "You'll be signed out soon" in rendered
