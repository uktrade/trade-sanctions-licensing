import pytest
from apply_for_a_licence.choices import (
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
    YesNoDoNotKnowChoices,
)
from apply_for_a_licence.models import Licence, Organisation
from django.test import RequestFactory
from django.urls import reverse


class TestSubmitterReferenceView:
    def test_post(self, authenticated_al_client):
        assert Licence.objects.count() == 0
        request = RequestFactory().get("/")
        request.session = authenticated_al_client.session
        response = authenticated_al_client.post(reverse("submitter_reference"), data={"submitter_reference": "test"})

        assert response.status_code == 302
        assert "start" in response.url
        assert Licence.objects.count() == 1
        assert Licence.objects.first().submitter_reference == "test"
        assert Licence.objects.first().pk == request.session["licence_id"]
        assert response.url == reverse("start", kwargs={"pk": request.session["licence_id"]})


@pytest.mark.django_db
class TestStartView:
    def test_post_myself(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
        )
        session = authenticated_al_client.session
        session.update({"licence_id": licence.id})
        session.save()
        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.who_do_you_want_the_licence_to_cover == "myself"
        assert "task-list" in response.url

    def test_post_business(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
        )
        session = authenticated_al_client.session
        session.update({"licence_id": licence.id})
        session.save()
        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.business.value},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.who_do_you_want_the_licence_to_cover == "business"
        assert response.url == reverse("tasklist")

    def test_licence_data_delete(self, authenticated_al_client, test_apply_user):
        # Create the licence
        licence = Licence.objects.create(
            user=test_apply_user,
        )
        session = authenticated_al_client.session
        session.update({"licence_id": licence.id})
        session.save()

        authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data={"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.business.value},
        )

        # Change the user's original answer to who_do_you_want_the_licence_to_cover
        new_choice = {"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value}
        response = authenticated_al_client.post(
            reverse("start", kwargs={"pk": licence.id}),
            data=new_choice,
        )

        # ensure the form redirects and the original licence no longer exists
        assert response.status_code == 302
        with pytest.raises(Licence.DoesNotExist):
            Licence.objects.get(pk=licence.id)

        assert response.url == reverse("tasklist")

    def test_licence_delete_other_entities(self, authenticated_al_client_with_licence, test_apply_user):
        # Create the licence and session obj
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )
        session = authenticated_al_client_with_licence.session
        session.update({"licence_id": licence.id})
        session.save()

        # Create the associated org object from the newly create licence
        Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )

        assert Organisation.objects.filter(licence=licence).exists()

        # Now change the users answer to who_do_you_want_the_licence_to_cover
        new_choice = {"who_do_you_want_the_licence_to_cover": WhoDoYouWantTheLicenceToCoverChoices.myself.value}
        authenticated_al_client_with_licence.post(
            reverse("start", kwargs={"pk": licence.id}),
            data=new_choice,
        )

        # ensure that the original licence and organisation no longer exists
        with pytest.raises(Organisation.DoesNotExist):
            Organisation.objects.get(pk=licence.id)

        with pytest.raises(Licence.DoesNotExist):
            Licence.objects.get(pk=licence.id)


class TestThirdPartyView:
    def test_post_third_party_individual(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": True},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.is_third_party
        assert response.url == reverse("your_details")

    def test_post_third_party_business(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": True},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.is_third_party
        assert response.url == reverse("your_details")

    def test_post_not_third_party_individual(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value
        )
        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": False},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert not licence_response.is_third_party
        assert "your-details" in response.url

    def test_post_not_third_party_business(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("are_you_third_party"),
            data={"is_third_party": False},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert not licence_response.is_third_party
        assert "your-details" in response.url


class TestYourDetailsView:
    def test_post_individual(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
            is_third_party=True,
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.individual.value,
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("your_details"),
            data={"applicant_full_name": "John Smith", "applicant_business": "PBS", "applicant_role": "role 1"},
        )
        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.applicant_role == "role 1"
        assert "task-list" in response.url

    def test_post_business(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user,
            is_third_party=True,
            who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value,
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("your_details"),
            data={"applicant_full_name": "John Smith", "applicant_business": "PBS", "applicant_role": "role 2"},
        )

        assert response.status_code == 302
        licence_response = Licence.objects.get(pk=licence.id)
        assert licence_response.applicant_role == "role 2"
        assert "task-list" in response.url
