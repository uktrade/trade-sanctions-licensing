import uuid

from apply_for_a_licence.choices import (
    TypeOfRelationshipChoices,
    WhoDoYouWantTheLicenceToCoverChoices,
    YesNoChoices,
    YesNoDoNotKnowChoices,
)
from apply_for_a_licence.models import Licence, Organisation
from django.urls import reverse


class TestIsTheBusinessRegisteredWithCompaniesHouse:
    def test_business_not_registered_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house", kwargs={"business_uuid": uuid.uuid4()}),
            data={"business_registered_on_companies_house": "no"},
            follow=True,
        )
        assert reverse("where_is_the_business_located", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_business_registered_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        business_uuid = uuid.uuid4()
        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house", kwargs={"business_uuid": business_uuid}),
            data={"business_registered_on_companies_house": "yes"},
        )
        assert response.url == reverse("do_you_know_the_registered_company_number", kwargs={"business_uuid": business_uuid})


class TestDoYouKnowTheRegisteredCompanyNumber:
    def test_know_the_registered_company_number_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )
        response = authenticated_al_client.post(
            reverse("do_you_know_the_registered_company_number", kwargs={"business_uuid": business.id}),
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
        )
        assert (
            reverse("do_you_know_the_registered_company_number", kwargs=response.resolver_match.kwargs)
            in response.wsgi_request.path
        )

    def test_do_not_know_the_registered_company_number_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )
        response = authenticated_al_client.post(
            reverse("do_you_know_the_registered_company_number", kwargs={"business_uuid": business.id}),
            data={"do_you_know_the_registered_company_number": "no"},
            follow=True,
        )
        assert reverse("where_is_the_business_located", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_get_context_data(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )
        response = authenticated_al_client.get(
            reverse("do_you_know_the_registered_company_number", kwargs={"business_uuid": business.id})
        )
        assert response.context["page_title"] == "Registered Company Number"


class TestBusinessAddedView:
    def test_do_not_add_business_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create at least 1 business
        Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": False},
        )
        assert response.url == reverse("previous_licence")

    def test_add_another_business_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create at least 1 business
        Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": True},
        )
        assert "business-registered-with-companies-house" in response.url
        assert "?change=yes" in response.url


class TestDeleteBusinessView:
    def test_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 2 businesses
        business1 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business2 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        response = authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_uuid": business1.id}),
        )
        businesses = Organisation.objects.filter(licence=licence)

        assert business1 not in businesses
        assert business2 in businesses
        assert response.url == "/apply/add-business"
        assert response.status_code == 302

    def test_cannot_delete_all_businesses_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 3 businesses
        business1 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business2 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business3 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_uuid": business1.id}),
        )
        authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_uuid": business2.id}),
        )
        response = authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_uuid": business3.id}),
        )
        businesses = Organisation.objects.filter(licence=licence)
        # does not delete last business
        assert len(businesses) == 1
        assert business1 not in businesses
        assert business2 not in businesses
        assert business3 in businesses
        assert response.status_code == 404

    def test_unsuccessful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 3 businesses
        business1 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business2 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business3 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        response = authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_uuid": uuid.uuid4()}),
        )
        businesses = Organisation.objects.filter(licence=licence)
        # does not delete any business
        assert len(businesses) == 3
        assert business1 in businesses
        assert business2 in businesses
        assert business3 in businesses
        assert response.status_code == 404


class TestCheckCompanyDetailsView:
    def test_check_successful_post(self, request_object, authenticated_al_client, test_apply_user):
        request_object.session = authenticated_al_client.session
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 3 businesses
        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
            do_you_know_the_registered_company_number=YesNoChoices.yes,
            registered_company_number=1234567,
            name="Test company",
            registered_office_address="AL1, United Kingdom",
        )
        response = authenticated_al_client.post(reverse("check_company_details", kwargs={"business_uuid": business.id}))
        assert response.url == "/apply/add-business"

    def test_get_context_data(self, request_object, authenticated_al_client, test_apply_user):
        request_object.session = authenticated_al_client.session
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 3 businesses
        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
            type_of_relationship=TypeOfRelationshipChoices.business,
            do_you_know_the_registered_company_number=YesNoChoices.yes,
            registered_company_number=1234567,
            name="Test company",
            registered_office_address="AL1, United Kingdom",
        )
        response = authenticated_al_client.get(reverse("check_company_details", kwargs={"business_uuid": business.id}))
        assert response.context["business"] == business
