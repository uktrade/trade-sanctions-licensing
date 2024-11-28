from crispy_forms_gds.layout import Field
from feedback.crispy_fields import HTMLTemplate, get_field_with_label_id
from feedback.forms import FeedbackForm


def test_html_template(request_object):
    layout = HTMLTemplate(
        html_template_path="apply_for_a_licence/form_steps/partials/not_received_code_help_text.html",
        html_context={"request_verify_code": "123456", "request": request_object},
    )
    rendered = layout.render(FeedbackForm())
    assert "123456" in rendered


def test_get_field_with_label_id():
    field = get_field_with_label_id("test_field", field_method=Field.textarea, label_id="test_id")
    assert field.context["label_id"] == "test_id"
