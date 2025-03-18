from crispy_forms_gds.layout import Field
from feedback.crispy_fields import HTMLTemplate, get_field_with_label_id
from feedback.forms import FeedbackForm


def test_html_template(request_object):
    layout = HTMLTemplate(
        html_template_path="feedback/participate_in_user_research.html",
        html_context={"request": request_object},
    )
    rendered = layout.render(FeedbackForm())
    assert "Participating in further research" in rendered


def test_get_field_with_label_id():
    field = get_field_with_label_id("test_field", field_method=Field.textarea, label_id="test_id")
    assert field.context["label_id"] == "test_id"
