from apply_for_a_licence.models import Licence
from apply_for_a_licence.views.views_business import BusinessAddedView
from apply_for_a_licence.views.views_start import SubmitterReferenceView
from django.test import RequestFactory
from django.urls import reverse


class TestBaseLicenceFormView:
    def test_incorrect_user_get_form_kwargs(self, authenticated_al_client):
        licence = Licence.objects.create(user=None)

        response = authenticated_al_client.get(
            reverse("your_details", kwargs={"licence_pk": licence.id}),
        )

        assert response.status_code == 404

    def test_correct_user_get_form_kwargs(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(user=test_apply_user)

        response = authenticated_al_client.get(
            reverse("your_details", kwargs={"licence_pk": licence.id}),
        )

        assert response.status_code == 200


class TestRedirectBaseDomainView:
    def test_redirect_apply_site(self, authenticated_al_client):
        response = authenticated_al_client.get("/")
        assert response.status_code == 302
        assert response.url == reverse("dashboard")

    def test_redirect_view_site(self, vl_client_logged_in):
        response = vl_client_logged_in.get("/")
        assert response.status_code == 302
        assert response.url == reverse("view_a_licence:application_list")


class TestBaseSaveAndReturnView:
    def test_post_skip_link_with_licence(self, licence_application, test_apply_user):
        request = RequestFactory().post(reverse("business_added", kwargs={"licence_pk": licence_application.id}))
        request.POST = {"skip_link": "yes"}
        request.user = test_apply_user
        view = BusinessAddedView()
        view.setup(request, licence_pk=licence_application.id)
        response = view.post(request, data={"do_you_want_to_add_another_business": False})

        assert response.url == reverse("tasklist", kwargs={"licence_pk": licence_application.id})

    def test_post_skip_link_nonexisting_licence(self):

        request = RequestFactory().post(reverse("submitter_reference"))
        request.POST = {"skip_link": "yes"}

        view = SubmitterReferenceView()
        view.setup(request)
        response = view.post(request, data={"submitter_reference": "ABC"})
        assert response.url == reverse("dashboard")
