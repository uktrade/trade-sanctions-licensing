from crispy_forms_gds.helper import FormHelper
from crispy_forms_gds.layout import Layout, Size, Submit
from django import forms


class EmptyForm(forms.Form):
    pass


class BaseForm(forms.Form):
    bold_labels = True
    form_h1_header = None
    single_question_form = False
    show_back_button = True
    # fields that you don't want to display (optional) next to the label if they're not required
    hide_optional_label_fields = []
    # if we're using a BaseForm and NOT a BaseModelForm, then we need to implement our own labels dictionary to set the labels
    labels = {}
    # same for help_texts
    help_texts = {}
    # do we want this form to be revalidated when the user clicks Done
    revalidate_on_done = True

    class Media:
        css = {
            "all": ["form.css"],
        }

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.request = kwargs.pop("request", None)
        self.form_h1_header = kwargs.pop("form_h1_header", self.form_h1_header)
        super().__init__(*args, **kwargs)

        if len(self.fields) == 1:
            self.single_question_form = True

        for field_name, label in self.labels.items():
            self.fields[field_name].label = label

        for field_name, help_text in self.help_texts.items():
            self.fields[field_name].help_text = help_text

        self.helper = FormHelper()
        self.helper.add_input(Submit("continue", "Continue", css_class="btn-primary"))

        if self.single_question_form and not self.form_h1_header:
            self.helper.label_tag = "h1"
            self.helper.legend_tag = "h1"
            self.helper.legend_size = Size.LARGE

        if self.bold_labels:
            self.helper.label_size = Size.LARGE

        self.helper.layout = Layout(*self.fields)


class BaseModelForm(BaseForm, forms.ModelForm):
    pass
