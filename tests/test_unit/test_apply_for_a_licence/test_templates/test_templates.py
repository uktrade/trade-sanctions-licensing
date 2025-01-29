from unittest.mock import MagicMock

from crispy_forms_gds.helper import FormHelper
from django.template.loader import get_template

from tests.helpers import get_all_templates_files_for_app


def test_all_templates_inherit_from_base_logged_in_template(request_object):
    app_name = "apply_for_a_licence"

    apply_templates = get_all_templates_files_for_app(app_name)
    for template in apply_templates:
        if "partials" in template.parts:
            continue
        else:
            django_template_object = get_template(template)
            context = {
                "request": request_object,
                "form": MagicMock(helper=MagicMock(spec_set=FormHelper, template="apply_for_a_licence/complete.html")),
            }
            rendered = django_template_object.render(context, request_object)
            assert "session_expiry_dialog" in rendered
            assert "You'll be signed out soon" in rendered
