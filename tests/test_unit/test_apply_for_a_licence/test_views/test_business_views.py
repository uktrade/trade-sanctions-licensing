from unittest.mock import patch

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
        business = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house") + f"?business_id={business.id}",
            data={"business_registered_on_companies_house": "no"},
            follow=True,
        )
        assert reverse("where_is_the_business_located", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_business_registered_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )
        business = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        response = authenticated_al_client.post(
            reverse("is_the_business_registered_with_companies_house") + f"?business_id={business.id}",
            data={"business_registered_on_companies_house": "yes"},
        )
        assert response.url == reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id})

    def test_create_new_business_successful_get(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )
        licence_businesses = Organisation.objects.filter(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        assert len(licence_businesses) == 0

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        authenticated_al_client.get(
            reverse("is_the_business_registered_with_companies_house") + "?new=yes",
        )
        licence_businesses = Organisation.objects.filter(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        assert len(licence_businesses) == 1
        assert licence_businesses[0].status == "draft"

    def test_no_business_id_returns_404(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        response = authenticated_al_client.get(
            reverse("is_the_business_registered_with_companies_house"),
        )
        licence_businesses = Organisation.objects.filter(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        assert len(licence_businesses) == 0
        assert response.status_code == 404


class TestDoYouKnowTheRegisteredCompanyNumberView:
    def test_know_the_registered_company_number_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business
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
            reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id}),
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
            reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id}),
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
            reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id})
        )
        assert response.context["page_title"] == "Registered Company Number"

    @patch("apply_for_a_licence.forms.forms_business.get_details_from_companies_house")
    @patch("apply_for_a_licence.forms.forms_business.get_formatted_address")
    def test_setting_do_you_know_the_registered_company_number(
        self,
        mocked_get_formatted_address,
        mocked_get_details_from_companies_house,
        authenticated_al_client_with_licence,
        licence_application,
    ):
        mocked_get_details_from_companies_house.return_value = {
            "company_number": "12345678",
            "company_name": "Test Company",
            "registered_office_address": "",
        }
        mocked_get_formatted_address.return_value = "12 road, London"

        licence_application.who_do_you_want_the_licence_to_cover = WhoDoYouWantTheLicenceToCoverChoices.business.value
        licence_application.save()

        business = Organisation.objects.create(
            licence=licence_application,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.no,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )
        assert not business.do_you_know_the_registered_company_number
        authenticated_al_client_with_licence.post(
            reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id}),
            data={"do_you_know_the_registered_company_number": "yes", "registered_company_number": "12345678"},
            follow=True,
        )

        business.refresh_from_db()
        assert business.do_you_know_the_registered_company_number


class TestBusinessAddedView:
    def test_redirect_if_no_business(self, authenticated_al_client):
        response = authenticated_al_client.get(
            reverse("business_added"),
        )
        assert "task-list" in response.url
        assert response.status_code == 302

    def test_do_not_add_business_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create at least 1 business
        Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business, status="complete")

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": False},
        )
        assert response.url == reverse("tasklist")

    def test_add_another_business_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create at least 1 business
        Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business, status="complete")

        response = authenticated_al_client.post(
            reverse("business_added"),
            data={"do_you_want_to_add_another_business": True},
        )
        assert "business-registered-with-companies-house" in response.url

    def test_get_context_data(self, authenticated_al_client, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        response = authenticated_al_client.get(reverse("business_added"))
        assert response.context["businesses"][0] == organisation


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
            reverse("delete_business", kwargs={"business_id": business1.id}),
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
            reverse("delete_business", kwargs={"business_id": business1.id}),
        )
        authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_id": business2.id}),
        )
        response = authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_id": business3.id}),
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
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()
        # create 3 businesses
        business1 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business2 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        business3 = Organisation.objects.create(licence=licence, type_of_relationship=TypeOfRelationshipChoices.business)
        response = authenticated_al_client.post(
            reverse("delete_business", kwargs={"business_id": 111111}),
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
        response = authenticated_al_client.post(reverse("check_company_details", kwargs={"business_id": business.id}))
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
        response = authenticated_al_client.get(reverse("check_company_details", kwargs={"business_id": business.id}))
        assert response.context["business"] == business


class TestAddABusinessView:
    def test_successful_post_uk_business(self, authenticated_al_client, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        assert not organisation.country
        assert not organisation.address_line_1
        assert not organisation.county
        assert not organisation.town_or_city
        assert not organisation.postcode

        response = authenticated_al_client.post(
            reverse(
                "add_a_business",
                kwargs={"location": "in-uk", "business_id": organisation.id},
            ),
            data={
                "name": "DBT",
                "country": "GB",
                "address_line_1": "new address 1",
                "address_line_2": "new address 2",
                "county": "Greater London",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )

        assert response.url == reverse("business_added")
        organisation = Organisation.objects.get(id=organisation.id)
        assert organisation.country == "GB"
        assert organisation.address_line_1 == "new address 1"
        assert organisation.county == "Greater London"
        assert organisation.town_or_city == "City"
        assert organisation.postcode == "SW1A 1AA"

    def test_successful_post_non_uk_business(self, authenticated_al_client, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        assert not organisation.country
        assert not organisation.address_line_1
        assert not organisation.town_or_city

        response = authenticated_al_client.post(
            reverse(
                "add_a_business",
                kwargs={"location": "outside-uk", "business_id": organisation.id},
            ),
            data={
                "name": "DBT",
                "country": "NL",
                "address_line_1": "Dutch address",
                "town_or_city": "Dutch City",
            },
        )

        assert response.url == reverse("business_added")
        organisation = Organisation.objects.get(id=organisation.id)
        assert organisation.country == "NL"
        assert organisation.address_line_1 == "Dutch address"
        assert organisation.town_or_city == "Dutch City"

    def test_get_form_data(self, authenticated_al_client, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        response = authenticated_al_client.get(
            reverse(
                "add_a_business",
                kwargs={
                    "location": "in-uk",
                    "business_id": organisation.id,
                },
            )
        )
        assert not response.context["form"].is_bound

    def test_get_success_url(self, authenticated_al_client, licence, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        licence.who_do_you_want_the_licence_to_cover = WhoDoYouWantTheLicenceToCoverChoices.business
        licence.save()

        response = authenticated_al_client.post(
            reverse(
                "add_a_business",
                kwargs={
                    "location": "in-uk",
                    "business_id": organisation.id,
                },
            ),
            data={
                "name": "DBT",
                "country": "GB",
                "address_line_1": "new address 1",
                "address_line_2": "new address 2",
                "county": "Greater London",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )

        assert response.url == reverse("business_added")

    def test_save_form(self, authenticated_al_client, licence_application, organisation):
        organisation.type_of_relationship = "business"
        organisation.save()
        licence_application.who_do_you_want_the_licence_to_cover = WhoDoYouWantTheLicenceToCoverChoices.business
        licence_application.save()
        authenticated_al_client.post(
            reverse(
                "add_a_business",
                kwargs={
                    "location": "in-uk",
                    "business_id": organisation.id,
                },
            ),
            data={
                "name": "DBT",
                "country": "GB",
                "address_line_1": "new address 1",
                "town_or_city": "City",
                "postcode": "SW1A 1AA",
            },
        )
        businesses = Organisation.objects.filter(
            licence=licence_application,
        )
        assert len(businesses) == 1
        assert businesses[0].status == "complete"
        assert businesses[0].name == "DBT"


class TestManualCompaniesHouseInputView:
    # todo: fix test - issue is with sessions
    # def test_manual_companies_house_successful_post(self, al_client, test_apply_user):
    #     licence = Licence.objects.create(
    #         user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
    #     )
    #
    #     session = al_client.session
    #     session["licence_id"] = licence.id
    #     session["company_details_500"] = True
    #     session.save()
    #     business = Organisation.objects.create(
    #         licence=licence,
    #         business_registered_on_companies_house=YesNoDoNotKnowChoices.yes,
    #         type_of_relationship=TypeOfRelationshipChoices.business,
    #     )
    #     response = al_client.post(
    #         reverse("do_you_know_the_registered_company_number", kwargs={"business_id": business.id}),
    #         data={"do_you_know_the_registered_company_number": "yes"},
    #         follow=True,
    #     )
    #     assert reverse("manual_companies_house_input", kwargs=response.resolver_match.kwargs) in response.wsgi_request.path

    def test_manual_companies_house_input_successful_post(self, authenticated_al_client, test_apply_user):
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
            reverse("manual_companies_house_input", kwargs={"business_id": business.id}),
            data={"where_is_the_address": "in-uk"},
            follow=True,
        )
        assert reverse("add_a_business", kwargs={"business_id": business.id, "location": "in-uk"}) in response.wsgi_request.path


class TestWhereIsTheBusinessLocatedView:
    def test_successful_post(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.no,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )
        response = authenticated_al_client.post(
            reverse("where_is_the_business_located", kwargs={"business_id": business.id}),
            data={"where_is_the_address": "in-uk"},
            follow=True,
        )
        assert reverse("add_a_business", kwargs={"business_id": business.id, "location": "in-uk"}) in response.wsgi_request.path

    def test_clears_form_data(self, authenticated_al_client, test_apply_user):
        licence = Licence.objects.create(
            user=test_apply_user, who_do_you_want_the_licence_to_cover=WhoDoYouWantTheLicenceToCoverChoices.business.value
        )

        session = authenticated_al_client.session
        session["licence_id"] = licence.id
        session.save()

        business = Organisation.objects.create(
            licence=licence,
            business_registered_on_companies_house=YesNoDoNotKnowChoices.no,
            type_of_relationship=TypeOfRelationshipChoices.business,
        )

        authenticated_al_client.post(
            reverse("where_is_the_business_located", kwargs={"business_id": business.id}),
            data={"where_is_the_address": "outside-uk"},
        )

        # input business details
        response = authenticated_al_client.post(
            reverse(
                "add_a_business",
                kwargs={"location": "outside-uk", "business_id": business.id},
            ),
            data={
                "name": "DBT",
                "country": "NL",
                "address_line_1": "Dutch address",
                "town_or_city": "Dutch City",
            },
        )

        assert response.url == reverse("business_added")

        business = Organisation.objects.get(id=business.id)
        assert business.name == "DBT"
        assert business.country == "NL"
        assert business.address_line_1 == "Dutch address"
        assert business.town_or_city == "Dutch City"
        # change address to uk
        authenticated_al_client.post(
            reverse("where_is_the_business_located", kwargs={"business_id": business.id}),
            data={"where_is_the_address": "in-uk"},
            follow=True,
        )
        # assert business address details cleared
        business = Organisation.objects.get(id=business.id)
        assert not business.address_line_1
        assert not business.country
        assert not business.town_or_city
        assert business.name == "DBT"
