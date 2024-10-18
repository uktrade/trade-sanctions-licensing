from typing import Any

from apply_for_a_licence import choices
from apply_for_a_licence.choices import TypeOfRelationshipChoices
from apply_for_a_licence.exceptions import EmailNotVerifiedException
from apply_for_a_licence.models import (
    Document,
    Individual,
    Licence,
    Organisation,
    UserEmailVerification,
)
from core.document_storage import TemporaryDocumentStorage
from django.http import HttpRequest

from .s3 import get_all_session_files, store_document_in_permanent_bucket


class SaveToDB:
    def __init__(
        self,
        request: HttpRequest,
        data: dict[str, Any],
        is_individual: bool,
        is_third_party: bool,
        is_on_companies_house: bool,
    ) -> None:
        self.request = request
        self.email_verification = self._get_user_verification()
        self.data = data
        self.is_individual = is_individual
        self.is_third_party = is_third_party
        self.is_on_companies_house = is_on_companies_house

    def _get_user_verification(self) -> UserEmailVerification:
        user_email_verification = UserEmailVerification.objects.filter(user_session=self.request.session.session_key).latest(
            "date_created"
        )

        if not user_email_verification.verified:
            # the user hasn't verified their email address, don't let them submit
            raise EmailNotVerifiedException()
        return user_email_verification

    def save_licence(self) -> Licence:
        sanctions_regimes = []
        if self.data["which_sanctions_regime"]:
            sanctions_regimes = self.data["which_sanctions_regime"]["which_sanctions_regime"]

        licence = Licence.objects.create(
            applicant_user_email_address=self.data["what_is_your_email"]["email"],
            licensing_grounds=self.data["licensing_grounds"].get("licensing_grounds"),
            licensing_grounds_legal_advisory=self.data["licensing_grounds_legal_advisory"].get("licensing_grounds"),
            business_registered_on_companies_house="Yes" if self.is_on_companies_house else "No",
            regimes=sanctions_regimes,
            type_of_service=self.data["type_of_service"]["type_of_service"],
            professional_or_business_services=self.data.get("professional_or_business_services").get(
                "professional_or_business_services"
            ),
            service_activities=self.data["service_activities"]["service_activities"],
            purpose_of_provision=self.data["purpose_of_provision"]["purpose_of_provision"],
            held_existing_licence=self.data["previous_licence"]["held_existing_licence"],
            existing_licences=self.data["previous_licence"]["existing_licences"],
            is_third_party=self.is_third_party,
            user_email_verification=self.email_verification,
            who_do_you_want_the_licence_to_cover=self.data["start"]["who_do_you_want_the_licence_to_cover"],
        )

        if self.data["start"]["who_do_you_want_the_licence_to_cover"] == "myself":
            licence.applicant_full_name = f"{self.data['add_yourself']['first_name']} {self.data['add_yourself']['last_name']}"
        else:
            licence.applicant_role = self.data["your_details"]["applicant_role"]
            licence.applicant_business = self.data["your_details"]["applicant_business"]
            licence.applicant_full_name = self.data["your_details"]["applicant_full_name"]

        licence.assign_reference()
        licence.save()

        self.licence_object = licence
        return licence

    def save_individuals(self) -> None:
        for _, individual in self.request.session.get("individuals", {}).items():
            Individual.objects.create(
                licence=self.licence_object,
                first_name=individual["name_data"]["cleaned_data"]["first_name"],
                last_name=individual["name_data"]["cleaned_data"]["last_name"],
                nationality_and_location=individual["name_data"]["cleaned_data"]["nationality_and_location"],
                address_line_1=individual["address_data"]["cleaned_data"]["address_line_1"],
                address_line_2=individual["address_data"]["cleaned_data"].get("address_line_2"),
                address_line_3=individual["address_data"]["cleaned_data"].get("address_line_3"),
                address_line_4=individual["address_data"]["cleaned_data"].get("address_line_4"),
                postcode=individual["address_data"]["cleaned_data"].get("postcode"),
                country=individual["address_data"]["cleaned_data"]["country"],
                town_or_city=individual["address_data"]["cleaned_data"]["town_or_city"],
                relationship_provider="",  # todo: fix,
            )

        if self.data["start"]["who_do_you_want_the_licence_to_cover"] == choices.WhoDoYouWantTheLicenceToCoverChoices.myself:
            # creating the additional individual (for the applicant)
            Individual.objects.create(
                licence=self.licence_object,
                first_name=self.data["add_yourself"]["first_name"],
                last_name=self.data["add_yourself"]["last_name"],
                nationality_and_location=self.data["add_yourself"]["nationality_and_location"],
                address_line_1=self.data["add_yourself_address"]["address_line_1"],
                address_line_2=self.data["add_yourself_address"].get("address_line_2"),
                address_line_3=self.data["add_yourself_address"].get("address_line_3"),
                address_line_4=self.data["add_yourself_address"].get("address_line_4"),
                postcode=self.data["add_yourself_address"].get("postcode"),
                country=self.data["add_yourself_address"]["country"],
                town_or_city=self.data["add_yourself_address"].get("town_or_city"),
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )

    def save_business(self) -> None:
        # named individuals employment details
        if self.is_individual:
            Organisation.objects.create(
                licence=self.licence_object,
                name=self.data["business_employing_individual"]["name"],
                do_you_know_the_registered_company_number="No",
                address_line_1=self.data["business_employing_individual"]["address_line_1"],
                address_line_2=self.data["business_employing_individual"]["address_line_2"],
                address_line_3=self.data["business_employing_individual"]["address_line_3"],
                address_line_4=self.data["business_employing_individual"]["address_line_4"],
                country=self.data["business_employing_individual"]["country"],
                type_of_relationship=TypeOfRelationshipChoices.named_individuals,
                relationship_provider=self.data["relationship_provider_recipient"]["relationship"],
            )

        # business journey company details
        else:
            for _, business in self.request.session["businesses"].items():
                if business["cleaned_data"].get("companies_house"):
                    Organisation.objects.create(
                        licence=self.licence_object,
                        name=business["cleaned_data"]["name"],
                        do_you_know_the_registered_company_number=choices.YesNoChoices.yes,
                        registered_company_number=business["cleaned_data"]["company_number"],
                        registered_office_address=business["cleaned_data"]["readable_address"],
                        type_of_relationship=TypeOfRelationshipChoices.business,
                    )
                else:
                    Organisation.objects.create(
                        licence=self.licence_object,
                        do_you_know_the_registered_company_number=choices.YesNoChoices.no,
                        name=business["cleaned_data"]["name"],
                        address_line_1=business["cleaned_data"]["address_line_1"],
                        address_line_2=business["cleaned_data"].get("address_line_2"),
                        address_line_3=business["cleaned_data"].get("address_line_3"),
                        address_line_4=business["cleaned_data"].get("address_line_4"),
                        country=business["cleaned_data"]["country"],
                        type_of_relationship=choices.TypeOfRelationshipChoices.business,
                    )

    def save_recipient(self) -> None:
        for _, recipient in self.request.session["recipients"].items():
            cl = recipient["cleaned_data"]
            Organisation.objects.create(
                licence=self.licence_object,
                name=cl["name"],
                website=cl.get("website"),
                email=cl.get("email"),
                additional_contact_details=cl.get("additional_contact_details"),
                address_line_1=cl["address_line_1"],
                address_line_2=cl.get("address_line_2"),
                address_line_3=cl.get("address_line_3"),
                address_line_4=cl.get("address_line_4"),
                postcode=cl.get("postcode"),
                country=cl["country"],
                town_or_city=cl.get("town_or_city"),
                type_of_relationship=TypeOfRelationshipChoices.recipient,
                relationship_provider=recipient["relationship"],
            )

    def save_documents(self) -> None:
        documents = get_all_session_files(TemporaryDocumentStorage(), self.request.session)
        for key, _ in documents.items():
            new_key = store_document_in_permanent_bucket(object_key=key, licence_pk=self.licence_object.pk)

            Document.objects.create(
                licence=self.licence_object,
                file=new_key,
            )
