# class AddYourselfView(BaseFormView):
#     form_class = forms.AddYourselfForm
#     success_url = reverse_lazy("add_yourself_address")
#
#
# class AddYourselfAddressView(BaseFormView):
#     form_class = forms.AddYourselfAddressForm
#     success_url = reverse_lazy("yourself_and_individual_added")
#
#     def get_form_kwargs(self) -> dict[str, Any]:
#         kwargs = super().get_form_kwargs()
#
#         if add_yourself_view := self.request.session.get("add_yourself", False):
#             if add_yourself_view.get("nationality_and_location") in [
#                 "uk_national_uk_location",
#                 "dual_national_uk_location",
#                 "non_uk_national_uk_location",
#             ]:
#                 kwargs["is_uk_address"] = True
#         return kwargs
#
#     def form_valid(self, form: forms.AddYourselfAddressForm) -> HttpResponse:
#         your_address = {
#             "cleaned_data": form.cleaned_data,
#             "dirty_data": form.data,
#         }
#         self.request.session["your_address"] = your_address
#         return super().form_valid(form)
#
#


from django.test import RequestFactory
from django.urls import reverse

from . import data


class TestYourselfAndIndividualAddedView:
    def test_successful_post(self, afal_client):
        response = afal_client.post(
            reverse("yourself_and_individual_added"),
            data={"do_you_want_to_add_another_individual": "no"},
        )
        assert response.url == reverse("myself_and_individual_added")
        assert response.status_code == 201


class TestDeleteIndividualFromYourselfView:
    def test_successful_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["individuals"] = data.individuals
        individual_id = "individual1"
        request.session.save()
        response = afal_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": individual_id},
        )
        assert "individual1" not in afal_client.session["individuals"].keys()
        assert afal_client.session["individuals"] != data.individuals
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302

    def test_delete_all_individuals_post(self, afal_client):
        request = RequestFactory().post("/")
        request.session = afal_client.session
        request.session["individuals"] = data.individuals
        request.session.save()
        response = afal_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual1"},
        )
        response = afal_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual2"},
        )
        response = afal_client.post(
            reverse("delete_individual_from_yourself"),
            data={"individual_uuid": "individual3"},
        )
        # does not delete last individual
        assert len(afal_client.session["individuals"]) == 0
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302

    def test_unsuccessful_post(self, afal_client):
        request_object = RequestFactory().get("/")
        request_object.session = afal_client.session
        request_object.session["individuals"] = data.individuals
        request_object.session.save()
        response = afal_client.post(
            reverse("delete_individual_from_yourself"),
        )
        assert afal_client.session["individuals"] == data.individuals
        assert response.url == "/apply-for-a-licence/yourself_and_individual_added"
        assert response.status_code == 302
